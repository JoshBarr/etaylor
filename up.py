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
    PASSWORD='default'
))

app.config.from_envvar('UP_SETTINGS', silent=True)


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------

class Album(object):
    """
    A generic container for all the album stuff
    """
    question = 1
    title = "Up = Side A"
    artist = "E Taylor"
    genre = "Rap"
    year = "2014"
    composer = "Elliot Taylor"
    artwork_template = "/static/album/up.png"
    tracks = [
        {
            "filename": "/static/tracks/1-e-taylor-little-empire.mp3",
            "title": "Little Empire"
        },
        {
            "filename": "/static/tracks/2-e-taylor-back-you-up.mp3",
            "title": "Back You Up Feat. Bella Kalolo"
        },
        {
            "filename": "/static/tracks/3-e-taylor-ego.mp3",
            "title": "Ego"
        },
        {
            "filename": "/static/tracks/4-e-taylor-new-york-any-nickel.mp3",
            "title": "New York (Any Nickel)"

        },
        {
            "filename": "/static/tracks/5-e-taylor-central-park.mp3",
            "title": "Central Park"
        }
    ]


class Questions(object):
    def __init__(self):
        return None

    def get(self, q_id=1):
        db = get_db()
        cur = db.execute('SELECT question from questions where id = %s' % (q_id))
        entry = cur.fetchone()
        title = ""
        if (len(entry) > 0):
            title = entry[0]
        return title

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


# -----------------------------------------------------------------------------
# Forms
# -----------------------------------------------------------------------------

class QuestionForm(Form):
    question = TextAreaField('Your answer', [validators.Length(min=2, max=98)])


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

        shuffle(other_answers)

        image_path = '%sartwork-%s-500x500.png' % (self.output_path, answer_id)
        thumbnail_path = '%sartwork-%s-140x140.png' % (self.output_path, answer_id)
        
        with Image(filename=self.foreground_template) as original:
            with original.convert('png') as album_details:
                with Drawing() as draw:
                    with Color('white') as bg:
                        with Image(width=500, height=500, background=bg) as image:
                            

                            draw.font = 'static/fonts/league_gothic.otf'
                            draw.font_size = 40
                            counter = 0

                            for a in other_answers:
                                draw.text(0, counter, a)
                                counter = counter+40
                            
                            draw(image)
                            image.composite(album_details, left=0, top=0)

                            image.save(filename=image_path)

        with Image(filename=image_path) as large:
            

        return self.store(answer_id, image_path, thumbnail_path)


    def store(self, answer_id, image_path, thumbnail_path):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT into artwork (answer_id, fullsize_url, thumbnail_url) values (?,?,?)',
                 [answer_id, image_path, thumbnail_path])
        db.commit()
        return cursor.lastrowid

    def get(self, artwork_id=1):
        db = get_db()
        cur = db.execute('SELECT fullsize_url, thumbnail_url from artwork where id = %s' % (artwork_id))
        entry = cur.fetchone()
        try:
            return {
                "full": entry[0],
                "thumb": entry[1]
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
    form = QuestionForm(request.form)
    email_form = EmailForm(request.form)
    album = Album()
    question = Questions().get(album.question)

    return render_template('up.j2', form=form, email_form=email_form, album=album, question=question)


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        if request.form:
            form = QuestionForm(request.form)
            if form.validate():
                album = Album()
                artwork = AlbumArtwork()
                answers = Answers()
                random_answers = answers.get_random_answers()
                answer_id = answers.store(form.question.data, album.question)
                unique_cover_id = artwork.render(form.question.data, answer_id, random_answers)
                return redirect('/download/%s' % (unique_cover_id))
            else:
                return redirect(url_for('start'))

    else:
        # If people try and access this directly, 
        # send them back home.
        return redirect(url_for('start'))


@app.route('/download', methods=['GET'])
def download():
    album = Album()
    return render_template('download.j2', album=album)

@app.route('/download/<int:artwork_id>')
def preview(artwork_id):
    album = AlbumArtwork().get(artwork_id)
    return render_template('download.j2', album=album)


@app.route('/share', methods=['GET', 'POST'])
def share():
    return render_template('email.j2')


@app.route('/email-me', methods=['GET', 'POST'])
def email():
    if request.method == "POST":
        if request.form:
            email_form = EmailForm(request.form)
            
            if email_form.validate():
                email = render_template('email.j2')
                session['music_video'] = True
                return redirect(url_for('music'))
            else:
                return redirect(url_for('start'))
    else:
        return {"response": "invalid"}


@app.route('/music-video', methods=['GET', 'POST'])
def music():
    if 'music_video' in session:
        session.pop('music_video', None)
        return render_template('music-video.j2')
    else:
        return redirect(url_for('start'))


# -----------------------------------------------------------------------------
# Init
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
