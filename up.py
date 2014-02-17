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

from concurrent import futures

# -----------------------------------------------------------------------------
# TODO
# -----------------------------------------------------------------------------
# 
# pretty album art
# ajaxy in-page stuff
# working... / taking to printer ... / drying ink... 


# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------

app = Flask(__name__)
CsrfProtect(app)

app.config.from_object(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'var/up.sqlite'),
    DEBUG=True,
    SECRET_KEY='\xcd\x8f\x14\xc1\x1f\xfd\xc8\xd04\xefl\xccEWWl8\xd3C\xa6\x99\x10\xc1A',
    USERNAME='admin',
    PASSWORD='default',


    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'e@thisisetaylor.com',
    MAIL_PASSWORD = 'HarryConnick67'
))




app.config.from_envvar('UP_SETTINGS', silent=True)
mail = Mail(app)


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

    def get_tracks(self):
        return self.tracks



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

    def get (self, answer_id):
        db = get_db()
        cur = db.execute('SELECT text, time, question_id from answers where id = %s' % (answer_id))
        entry = cur.fetchone()
        if (len(entry) > 0):
            text = entry[0]
            time = entry[1]
            question_id = entry[2]
            return {
                "id": answer_id,
                "text": text,
                "time": time,
                "question_id": question_id
            }
        else:
            return None



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
    question = TextAreaField('Your answer', [validators.Length(min=2, max=85, message='Your answer should be between 2 and 85 characters long.')])


class EmailForm(Form):
    email = TextField('Your email address', [validators.Email(message='Check that your email address is right')])


# -----------------------------------------------------------------------------
# Album artwork generator
# -----------------------------------------------------------------------------

class AlbumArtwork(object):
    artwork_template = "/static/album/up.png"
    foreground_template = "static/images/placeholder.png"
    image_output_path = "static/artwork/"
    track_input_path = "var/tracks/"
    track_temp_path = "var/download/"
    track_output_path = "static/tracks/"
    artwork = None
    image_path = None
    thumbnail_path = None
    zip_file_path = None
    
    def create(self, answer_id=None):
        self.answer_id = answer_id
        self.image_path = '%sartwork-%s-500x500.png' % (self.image_output_path, answer_id)
        self.thumbnail_path = '%sartwork-%s-140x140.png' % (self.image_output_path, answer_id)
        self.output_dir = "static/tracks/%s" % (answer_id)
        self.zip_file_path = "%s/e-taylor-up-side-a.zip" % (self.output_dir)
        self.artwor_id = self.store(self.answer_id, self.image_path, self.thumbnail_path, self.zip_file_path)
        return self

    def render(self, answer, answer_id, random_answers):

        all_answers = [answer]

        for row in random_answers:
            all_answers.append(row[0])

        shuffle(all_answers)

        image_path = self.image_path
        thumbnail_path = self.thumbnail_path
        
        with Image(filename=self.foreground_template) as original:
            with original.convert('png') as album_details:
                with Drawing() as draw:
                    with Color('white') as bg:
                        with Image(width=500, height=500, background=bg) as image:
                            
                            draw.font = 'static/fonts/league_gothic.otf'
                            draw.font_size = 40
                            counter = 40

                            _text = ". ".join(all_answers)

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

        self.process_tracks(answer_id, answer, image_path, thumbnail_path, self.zip_file_path)
        return self.zip_file_path 

    def copy_track(self, song, answer_id):
        song_input_filename = "%s%s" % (self.track_input_path, song['filename'])
        song_output_filename = "%s%s/%s" % (self.track_temp_path, answer_id, song['filename'])
        print "copying: ", song_input_filename, song_output_filename
        shutil.copy2(song_input_filename, song_output_filename)
        return song_output_filename

    def process_tracks(self, answer_id, answer, image_path, thumbnail_path, zip_output):
        output_dir = "%s%s" % (self.track_output_path, answer_id)
        temp_dir = "%s%s" % (self.track_temp_path, answer_id)
        image_data = open(image_path, "rb").read()
        thumbnail_data = open(thumbnail_path, "rb").read()

        # Get an album instance (they're all the mother flippin same...)
        album = Album()

        if not os.path.exists(zip_output):
            
            if not os.path.exists(temp_dir):
                mkdir_p(temp_dir)

            if not os.path.exists(output_dir):
                mkdir_p(output_dir)

            track_counter = 1;

            for song in album.tracks:
                song_output_filename = self.copy_track(song, answer_id)

                audiofile = eyed3.load(song_output_filename)
                print audiofile.tag

                if not audiofile.tag:
                    audiofile.tag = eyed3.id3.Tag()
                    audiofile.tag.file_info = eyed3.id3.FileInfo(song_output_filename)

                audiofile.tag.artist = u"%s" % ( album.artist )
                audiofile.tag.album = u"%s" % ( album.title )
                audiofile.tag.title = u"%s" % ( song['title'] )
                audiofile.tag.track_num = track_counter

                audiofile.tag.images.set(2, image_data, "image/png", u"%s - %s" % (album.artist, album.title))
                
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

    def store(self, answer_id, image_path, thumbnail_path, zip_file):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT or REPLACE into artwork (answer_id, fullsize_url, thumbnail_url, zip_file) values (?,?,?,?)',
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
            
    def get_by_answer(self, answer_id=1):
        db = get_db()
        cur = db.execute('SELECT id, fullsize_url, thumbnail_url, zip_file from artwork where answer_id = %s' % (answer_id))
        entry = cur.fetchone()
        try:
            return {
                "id": entry[0],
                "full": entry[1],
                "thumb": entry[2],
                "zip": entry[3]
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
                answers = Answers()
                answer_id = answers.store(form.question.data, album.question)
                return redirect('/share/%s' % (answer_id))
            else:
                errors.append("moo")

    return render_template('question.j2', form=form, album=album, question=question, errors=[])


@app.route('/share/<int:answer_id>')
def share(answer_id):
    questions = Questions()
    album = Album()
    answers = Answers()
    artwork = AlbumArtwork().create(answer_id)

    answer = answers.get(answer_id)
    random_answers = answers.get_random_answers()

    session["download"] = None

    executor = futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(async_do_render, artwork, answer["text"], answer_id, random_answers)
    future.add_done_callback(async_rendered)
    question = questions.get(album.question)

    return render_template('share.j2', question=question, answer=answer, artwork_id=answer_id)


@app.route('/download', methods=['GET'])
def download():
    return redirect(url_for('start'))


@app.route('/download/<int:answer_id>', methods=['GET', 'POST'])
def preview(answer_id):

    album = AlbumArtwork().get_by_answer(answer_id)
    email_form = EmailForm(request.form)
    errors = []

    session["download"] = request.url

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

    return render_template('download.j2', album=album, email_form=email_form, uid=answer_id, errors=errors)


def send_email(email, subject, body, html):
    """
    Send users a link to the album if they're accessing it from
    their phones/tablets
    """
    msg = Message(subject,
              sender=("E Taylor","e@thisisetaylor.com"),
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
    referrer = request.referrer
    return render_template('credits.j2', referrer=referrer)


# -----------------------------------------------------------------------------
# Events
# -----------------------------------------------------------------------------


def async_do_render(artwork, a, _id, ls):
    ctx = app.app_context()
    with app.app_context():

        res = artwork.render(a, _id, ls)        
        return res, ctx

def async_rendered(future):
    ctx = future.result()[1]

# -----------------------------------------------------------------------------
# Init
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
