from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, json, escape, make_response, send_from_directory, after_this_request,\
     current_app, Blueprint

from flask.ext.mail import Mail, Message

from up.forms import QuestionForm, EmailForm
from up.Models import Questions, Answers, Emails, db, Artwork
from up.Album import Album
from up.Artwork import AlbumArtwork
from up.cache import cache

from concurrent import futures

import shutil
import os
import datetime
import time

from random import shuffle


main = Blueprint("main", __name__)

executor = futures.ThreadPoolExecutor(max_workers=1)


# -----------------------------------------------
# Stuff to cache
# -----------------------------------------------

class AlbumModel:
    def __init__(self):
        self.album = Album()
        self.question = Questions.query.filter_by(id = self.album.question ).first()

    def get_question(self):
        return self.question

    def get(self):
        return self.album




@cache.cached(timeout=60, key_prefix='all_answers')
def get_random_answers():
    random_answers = Answers.query.limit(156).all()
    return random_answers




@main.route('/', methods=['GET', 'POST'])
@cache.cached(timeout=3600)
def start():
    return render_template('start.j2')







def create_answer(form_field, question):
    UP = AlbumModel()
    question = UP.get_question()
    random_answers = get_random_answers()
    shuffle(random_answers)

    answer = Answers(
            text = form_field.data,
            time = time.time(),
            question_id = question.id
        )


    db.session.add(answer)
    db.session.commit()

    hash_id = current_app.hashids.encrypt(answer.id)

    with AlbumArtwork() as artwork:
        print "creating artwork..."
        artwork.create(hash_id, answer, random_answers)
        artwork.render()

    
    session["download"] = None

    return render_template('share.j2', question=question, answer=answer, artwork_id=hash_id)



@main.route('/question', methods=['GET', 'POST'])
def question():
    errors = []
    form = QuestionForm(request.form)
    UP = AlbumModel()
    question = UP.get_question()


    if request.method == 'POST' and request.form:

        form = QuestionForm(request.form)
       
        if form.validate():

            with current_app.app_context():
                return create_answer(form.question, question)
            
            # return redirect('/share/%s' % (current_app.hashids.encrypt(answer_id)))
        
        else: pass

                 
    return render_template('question.j2', form=form, album=album, question=question, errors=[])


# @main.route('/share/<hash_id>')
# def share(hash_id):

    


@main.route('/download', methods=['GET'])
def download():
    return redirect(url_for('.start'))


@main.route('/download/<hash_id>', methods=['GET', 'POST'])
# @cache.cached(timeout=3600)
def preview(hash_id):

    answer_id = current_app.hashids.decrypt(hash_id)[0]

    album = Artwork.query.filter_by(answer_id=answer_id).first()
    email_form = EmailForm(request.form)
    errors = []

    session["download"] = request.url

    img = album.get_web_image()

    if request.method == "POST":
        if request.form:
            email_form = EmailForm(request.form)
            
            if email_form.validate():
                email_addy = email_form.email.data
                email_body = render_template('email-plain.j2', album_id=hash_id, email=email_addy)
                email_html = render_template('email.j2', album_id=hash_id, email=email_addy)
                send_email(
                    current_app,
                    email_addy,
                    " EP & artwork download from thisisetaylor.com",
                    email_body,
                    email_html
                )

                email = Emails(address=email_addy, time=time.time(), artwork_id=answer_id)

                db.session.add(email)
                db.session.commit()

                session['music_video'] = True
                return redirect(url_for('.music_video', hash_id = hash_id))
            
            else:
                errors.append("bad email addy")


    return render_template('download.j2', album=album, email_form=email_form, uid=hash_id, errors=errors, img=img)



@main.route('/ep/<hash_id>', methods=['GET'])
def album(hash_id):
    """
    Flask is great. Serve up a file, then run an after-request
    hook to clean up the files. Boom!
    """

    answer_id = current_app.hashids.decrypt(hash_id)[0]

    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    

    with AlbumArtwork() as artwork:
        album_filename = artwork.process(answer_id, hash_id)

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


def send_email(app, email, subject, body, html):
    """
    Send users a link to the album if they're accessing it from
    their phones/tablets
    """
    msg = Message(subject,
              sender=("E Taylor","e@thisisetaylor.com"),
              recipients=[email])
    msg.body = body
    msg.html = html
    app.mail.send(msg)


@main.route('/music-video/<hash_id>', methods=['GET', 'POST'])
@cache.cached(timeout=3600)
def music_video(hash_id):
    if 'music_video' in session:
        session.pop('music_video', None)
        return render_template('music-video.j2', album_id=hash_id)
    else:
        return redirect(url_for('.start'))


@main.route('/credits')
@cache.cached(timeout=3600)
def credits():
    referrer = request.referrer
    return render_template('credits.j2', referrer=referrer)


# -----------------------------------------------------------------------------
# Events
# -----------------------------------------------------------------------------


def async_do_render(app, artwork):
    ctx = app.app_context()
    with app.app_context():
        res = artwork.render()        
        return res, ctx

def async_rendered(future):
    pass
    # ctx = future.result()[1]
    # with ctx():
    #     print "foo"
    #     return ctx