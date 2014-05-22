import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, json, escape, make_response, send_from_directory, after_this_request
import os
import datetime
import time
from wtforms import Form, BooleanField, TextField, TextAreaField, validators   
from flask_wtf.csrf import CsrfProtect
from flask.ext.mail import Mail, Message

from concurrent import futures
import shutil


# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------

app = Flask(__name__)
CsrfProtect(app)

from Album import Album
from Artwork import AlbumArtwork
from Database import connect_db, get_db, close_db
from Models import Questions, Answers, Email


default_config = dict(
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
)

app.config.from_object("up.default_config")
app.config.from_pyfile("settings.py")
mail = Mail(app)


# -----------------------------------------------------------------------------
# Forms
# -----------------------------------------------------------------------------

class QuestionForm(Form):
    question = TextAreaField('Your answer', [validators.Length(min=2, max=85, message='Your answer should be between 2 and 85 characters long.')])


class EmailForm(Form):
    email = TextField('Your email address', [validators.Email(message='Check that your email address is right')])






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
    question = questions.get(album.question)
    answer = answers.get(answer_id)
    random_answers = answers.get_random_answers()

    session["download"] = None

    executor = futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(async_do_render, artwork, answer["text"], answer_id, random_answers)
    future.add_done_callback(async_rendered)
    
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

    # album['zip'] = album['zip'].replace("/static/", "/album/")

    # print album

    return render_template('download.j2', album=album, email_form=email_form, uid=answer_id, errors=errors)





from contextlib import contextmanager

@contextmanager
def serve_zip(path):
    zipfile = open(path)

    try:
        yield zipfile
    finally:
        zipfile.close()
        os.remove(path)


@app.route('/album/<int:answer_id>', methods=['GET'])
def album(answer_id):
    """
    Flask is great. Serve up a file, then run an after-request
    hook to clean up the files. Boom!
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    album_filename = AlbumArtwork().process(answer_id)
    base = os.path.commonprefix([current_dir, album_filename])
    path = album_filename.replace(base, "")

    _path, _file = os.path.split(album_filename)

    @after_this_request
    def add_header(response):
        try:
            shutil.rmtree(_path)
        except Exception:
            print "couldn't remove %s" % (_path) 
        return response;

    return send_from_directory(
        _path,
        _file,
        as_attachment=True
    )


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
    # app.run(host='0.0.0.0', debug = True)
    app.run(debug = True)
