import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, json, escape
import os
import yaml
import datetime
import time
from wtforms import Form, BooleanField, TextField, TextAreaField, validators   
from flask_wtf.csrf import CsrfProtect
from random import shuffle
from wand.image import Image
from wand.display import display
from wand.drawing import Drawing
from wand.color import Color
import textwrap
import eyed3
import shutil
import zipfile 
import errno

from flask.ext.mail import Mail, Message


# TODO
# 
# pretty album art
# email users
# save emails in database
# make it download zip file of tracks
# ajaxy in-page stuff
# working... / taking to printer ... / drying ink... 
# todo: hook up gmail 
# python -m smtpd -n -c DebuggingServer localhost:1025



# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------

MAIL_PORT=1025
MAIL_SERVER='localhost'

app = Flask(__name__)
CsrfProtect(app)


app.config.from_object(__name__)
mail = Mail(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'var/up.sqlite'),
    DEBUG=True,
    SECRET_KEY='\xcd\x8f\x14\xc1\x1f\xfd\xc8\xd04\xefl\xccEWWl8\xd3C\xa6\x99\x10\xc1A',
    USERNAME='admin',
    PASSWORD='default'
))

app.config.from_envvar('UP_SETTINGS', silent=True)

    


# Utils

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------

class Album(object):
    """
    A generic container for all the album stuff
    """
    question = 1
    title = "Up: Side A"
    artist = "E Taylor"
    genre = "Rap"
    year = "2014"
    composer = "Elliot Taylor"
    artwork_template = "/static/album/up.png"
    input_path = "var/tracks/"
    output_path = "static/tracks/"
    temp_path = "var/download/"
    tracks = [
        {
            "filename": "1-e-taylor-little-empire.mp3",
            "title": "Little Empire"
        },
        {
            "filename": "2-e-taylor-back-you-up.mp3",
            "title": "Back You Up Feat. Bella Kalolo"
        },
        {
            "filename": "3-e-taylor-ego.mp3",
            "title": "Ego"
        },
        {
            "filename": "4-e-taylor-new-york-any-nickel.mp3",
            "title": "New York (Any Nickel)"

        },
        {
            "filename": "5-e-taylor-central-park.mp3",
            "title": "Central Park"
        }
    ]

    def copy_track(self, song, answer_id):
        song_input_filename = "%s%s" % (self.input_path, song['filename'])
        song_output_filename = "%s%s/%s" % (self.temp_path, answer_id, song['filename'])
        shutil.copy2(song_input_filename, song_output_filename)
        return song_output_filename

    def process(self, answer_id, answer, image_path, thumbnail_path):
        output_dir = "%s%s" % (self.output_path, answer_id)
        temp_dir = "%s%s" % (self.temp_path, answer_id)
        image_data = open(image_path, "rb").read()
        thumbnail_data = open(thumbnail_path, "rb").read()
        zip_output = "%s/e-taylor-up-side-a.zip" % (output_dir)

        if not os.path.exists(zip_output):
            
            if not os.path.exists(temp_dir):
                mkdir_p(temp_dir)

            if not os.path.exists(output_dir):
                mkdir_p(output_dir)

            track_counter = 1;

            for song in self.tracks:
                song_output_filename = self.copy_track(song, answer_id)

                audiofile = eyed3.load(song_output_filename)
                audiofile.tag.artist = u"%s" % (self.artist)
                audiofile.tag.album = u"%s" % ( self.title )
                audiofile.tag.title = u"%s" % ( song['title'] )
                audiofile.tag.track_num = track_counter

                audiofile.tag.images.set(2,image_data,"image/png",u"%s - %s" % (self.artist, self.title))
                
                audiofile.tag.save()
                track_counter = track_counter + 1
            
            self.zip(temp_dir, zip_output)

        return zip_output


    def zip(self, src, dst):
        zf = zipfile.ZipFile("%s" % (dst), "w")
        abs_src = os.path.abspath(src)
        for dirname, subdirs, files in os.walk(src):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                print 'zipping %s as %s' % (os.path.join(dirname, filename),
                                            arcname)
                zf.write(absname, arcname)
        zf.close()
        shutil.rmtree(src)


class Questions(object):
    def __init__(self):
        return None

    def get(self, q_id=1):
        db = get_db()
        cur = db.execute('SELECT question, hashtag from questions where id = %s' % (q_id))
        entry = cur.fetchone()
        title = ""
        if (len(entry) > 0):
            title = entry[0]
            hashtag = entry[1]
        return {
            "title": title,
            "hashtag": hashtag
        }

class Answers(object):
    def __init__(self):
        return None

    def get_random_answers(self):
        db = get_db()
        cur = db.execute('SELECT text, time, question_id from answers limit 50')
        entries = cur.fetchall()
        shuffle(entries)
        return entries

    def store(self, answer, question_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute('INSERT into answers (text, time, question_id) values (?, ?, ?)',
                 [answer, time.time(), question_id])
        newid = cursor.lastrowid
        db.commit()
        return newid


class Email(object):
    def store(self, address, artwork_id):
        db = get_db()
        cursor = db.cursor()

        cursor.execute('INSERT into emails (address, time, artwork_id) values (?, ?, ?)',
                 [address, time.time(), artwork_id])
        newid = cursor.lastrowid
        db.commit()
        return newid



# -----------------------------------------------------------------------------
# Forms
# -----------------------------------------------------------------------------

class QuestionForm(Form):
    question = TextAreaField('Your answer', [validators.Length(min=2, max=85)])


class EmailForm(Form):
    email = TextField('Your email address', [validators.Email(message='Check that your email address is right')])


# -----------------------------------------------------------------------------
# Album artwork generator
# -----------------------------------------------------------------------------

class AlbumArtwork(object):
    artwork_template = "/static/album/up.png"
    foreground_template = "static/images/placeholder.png"
    artwork = None
    output_path = "static/artwork/"

    def render(self, answer, answer_id, random_answers):

        other_answers = [answer]

        for row in random_answers:
            other_answers.append(row[0])

        # shuffle(other_answers)

        image_path = '%sartwork-%s-500x500.png' % (self.output_path, answer_id)
        thumbnail_path = '%sartwork-%s-140x140.png' % (self.output_path, answer_id)
        
        with Image(filename=self.foreground_template) as original:
            with original.convert('png') as album_details:
                with Drawing() as draw:
                    with Color('white') as bg:
                        with Image(width=500, height=500, background=bg) as image:
                            

                            draw.font = 'static/fonts/league_gothic.otf'
                            draw.font_size = 40
                            counter = 40


                            _text = ". ".join(other_answers)

                            lines = textwrap.wrap(_text, 45)

                            for a in lines:
                                if counter < 440:
                                    draw.text(0, counter, a)
                                    counter = counter+40
                            
                            draw(image)
                            image.composite(album_details, left=0, top=0)

                            image.save(filename=image_path)

        with Image(filename=image_path) as large:
            with large.clone() as thumb:
                thumb.resize(140, 140)
                thumb.save(filename=thumbnail_path)

        zip_file = Album().process(answer_id, answer, image_path, thumbnail_path)

        return self.store(answer_id, image_path, thumbnail_path, zip_file)


    def store(self, answer_id, image_path, thumbnail_path, zip_file):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT into artwork (answer_id, fullsize_url, thumbnail_url, zip_file) values (?,?,?,?)',
                 [answer_id, image_path, thumbnail_path, zip_file])
        db.commit()
        return cursor.lastrowid

    def get(self, artwork_id=1):
        db = get_db()
        cur = db.execute('SELECT fullsize_url, thumbnail_url, zip_file from artwork where id = %s' % (artwork_id))
        entry = cur.fetchone()
        try:
            return {
                "full": entry[0],
                "thumb": entry[1],
                "zip": entry[2]
            }
        except:
            return None
            

# -----------------------------------------------------------------------------
# Database stuff
# -----------------------------------------------------------------------------

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# -----------------------------------------------------------------------------
# Routing
# -----------------------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('start.j2')


@app.route('/question', methods=['GET', 'POST'])
def question():
    errors = []
    form = QuestionForm(request.form)
    album = Album()
    question = Questions().get(album.question)

    if request.method == 'POST':

        if request.form:
            form = QuestionForm(request.form)
            if form.validate():
                artwork = AlbumArtwork()
                answers = Answers()
                random_answers = answers.get_random_answers()
                answer_id = answers.store(form.question.data, album.question)
                unique_cover_id = artwork.render(form.question.data, answer_id, random_answers)
                return redirect('/share/%s' % (unique_cover_id))
            else:
                errors.append("moo")

    return render_template('question.j2', form=form, album=album, question=question, errors=[])


@app.route('/share/<int:artwork_id>')
def share(artwork_id):
    album = AlbumArtwork().get(artwork_id)
    question = Questions().get(Album().question)
    return render_template('share.j2', question=question, uid=artwork_id)


@app.route('/download', methods=['GET'])
def download():
    return redirect(url_for('start'))

@app.route('/download/<int:artwork_id>', methods=['GET', 'POST'])
def preview(artwork_id):

    album = AlbumArtwork().get(artwork_id)
    email_form = EmailForm(request.form)
    errors = []

    if request.method == "POST":
        if request.form:
            email_form = EmailForm(request.form)
            
            if email_form.validate():
                email_addy = email_form.email.data
                email_body = render_template('email-plain.j2', album=album)
                email_html = render_template('email.j2', album=album)
                send_email(
                    email_addy,
                    "Album download from thisisetaylor.com",
                    email_body,
                    email_html
                )

                Email().store(email_addy, artwork_id)

                session['music_video'] = True
                return redirect(url_for('music_video'))
            else:
                errors.append("bad email addy")

    return render_template('download.j2', album=album, email_form=email_form, uid=artwork_id, errors=errors)


def send_email(email, subject, body, html):
    """
    Send users a link to the album if they're accessing it from
    their phones/tablets
    """
    msg = Message(subject,
              sender=("E Taylor","hello@thisisetaylor.com"),
              recipients=[email])
    msg.body = body
    msg.html = html

    # print msg

    mail.send(msg)


@app.route('/music-video', methods=['GET', 'POST'])
def music_video():
    if 'music_video' in session:
        session.pop('music_video', None)
        return render_template('music-video.j2')
    else:
        return redirect(url_for('start'))


@app.route('/credits')
def credits():
    return render_template('credits.j2')

# -----------------------------------------------------------------------------
# Init
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
