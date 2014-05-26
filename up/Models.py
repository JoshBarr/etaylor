from Database import connect_db, get_db, close_db
from random import shuffle
import time
import os

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

    def get_random_answers(self, not_this_id):
        db = get_db()
        cur = db.execute('SELECT text, time, question_id from answers  where id not in (%s) limit 156' % (not_this_id))
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