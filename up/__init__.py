from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, json, escape, make_response, send_from_directory, after_this_request

from flask_wtf.csrf import CsrfProtect
from flask.ext.mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from hashids import Hashids
from cache import cache


# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------

from Models import db
from controllers.main import main 



def create_app(settings_file):
    app = Flask(__name__)
    app.config.from_pyfile(settings_file)

    cache.init_app(app)

    mail = Mail()
    csrf = CsrfProtect()

    csrf.init_app(app)
    db.init_app(app)

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)

    app.mail = mail

    mail.init_app(app)

    app.hashids = Hashids(salt="salty seafaring sailor",  min_length=8)
    app.register_blueprint(main)
    
    return app


app = create_app("settings.py")