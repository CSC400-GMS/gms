import os


#Set environment
DEBUG = True

#Application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

#E-mail Server
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'grantms.notification@gmail.com'
MAIL_DEFAULT_SENDER = 'grantms.notification@gmail.com'
MAIL_PASSWORD = 'tuffpa55word'