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

def check_login(name):
    db = get_db()
    c = db.cursor()
    c.execute('select * from account where email =\''+ name+'\';')
    l = c.fetchall()
    if len(l) != 0:
        return True
    else:
        return False

def select_where(col, table, x, par):
    db = get_db()
    c = db.cursor()
    x = 'select '+col+' from '+table+' where '+x+'= \''+par+'\';'
    c.execute(x)
    l = c.fetchall()
    return l
