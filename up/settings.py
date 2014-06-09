import os

DEBUG = False

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ""))  


# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'var/up.sqlite')
DATABASE_CONNECT_OPTIONS = {}

# print SQLALCHEMY_DATABASE_URI

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "electricfence777"


SECRET_KEY='\xcd\x8f\x14\xc1\x1f\xfd\xc8\xd04\xefl\xccEWWl8\xd3C\xa6\x99\x10\xc1A'
USERNAME='admin'
PASSWORD='default'

MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME = 'e@thisisetaylor.com'
MAIL_PASSWORD = 'HarryConnick67'




CACHE_TYPE = 'simple'





