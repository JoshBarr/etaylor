from flask.ext.sqlalchemy import SQLAlchemy
import time
import os

db = SQLAlchemy()


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, )
    question = db.Column(db.Text())
    hashtag = db.Column(db.Text())


class Emails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, )
    address = db.Column(db.Text())
    time = db.Column(db.Float())
    artwork_id = db.Column(db.Integer, db.ForeignKey("artwork.id"))


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, )
    text = db.Column(db.Text())
    time = db.Column(db.Float())
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))


class Artwork(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, )
    answer_id = db.Column(db.Integer, db.ForeignKey("answers.id"))
    thumbnail_url = db.Column(db.Text())
    fullsize_url = db.Column(db.Text())
    fullsize_jpg = db.Column(db.Text())
    zip_file = db.Column(db.Text())

    def get_web_image(self):
        return os.path.split(self.fullsize_jpg)[1]





