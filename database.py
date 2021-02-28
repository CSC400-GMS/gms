import sqlite3
from flask import g

database = 'app.db'

def connection(db_file):
        con = sqlite3.connect(db_file)
        return con

def get_db():
        if 'db' not in g:
                g.db = connection(database)
        return g.db

def insert(sql, info):
	db = get_db()
	c = db.cursor()
	c.execute(sql, info)
	db.commit()
