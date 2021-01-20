import os

#Set environment
DEBUG = True

#Application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
