from flask import Flask, g
import sqlite3
from flask_bootstrap import Bootstrap
from flask_moment import Moment

app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY'] = 'hard to guess string'

database = "app.db"
bootstrap = Bootstrap(app)
moment = Moment(app)


def connection(db_file):
        con = sqlite3.connect(db_file)
        return con

def get_db():
    if 'db' not in g:
            g.db = connection(database)
    return g.db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'db'):
		g.db.close()
		print('closed the database')

def init_db():
	db = get_db()
	c = db.cursor()
	with app.open_resource('grant.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
	init_db()
	print('initialized the database')


import gms.routes
