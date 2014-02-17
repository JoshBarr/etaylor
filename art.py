"""
Processing in a nice language? So sweet!
"""

import os
# import sqlite3
# DATABASE=os.path.join(app.root_path, 'var/up.sqlite'),

# def get_random_answers(self):
#     db = get_db()
#     cur = db.execute('SELECT text, time, question_id from answers limit 50')
#     entries = cur.fetchall()
#     shuffle(entries)
#     return entries

# def connect_db():
#     """Connects to the specific database."""
#     rv = sqlite3.connect(DATABASE)
#     rv.row_factory = sqlite3.Row
#     return rv

# def get_db():
#     """Opens a new database connection if there is none yet for the
#     current application context.
#     """
#     if not hasattr(g, 'sqlite_db'):
#         g.sqlite_db = connect_db()
#     return g.sqlite_db

# print get_random_answers()





words = [
          "sometimes it's like", "the lines of text", "are so happy",
          "that they want to dance", "or leave the page or jump",
          "can you blame them?", "living on the page like that",
          "waiting to be read..."
        ]




def setup():
    size(500, 500)
    img = loadImage("test.png") # Load the original image
    image(img, 0, 0)             # Displays the image from point (0,0) 
    img.loadPixels();



def draw():
    ellipse(mouseX, mouseY, 10, 10)