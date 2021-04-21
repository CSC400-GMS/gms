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

def sql_script(sql):
	db = get_db()
	c = db.cursor()
	c.execute(sql)
	db.commit()


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

def select_all(table):
    db = get_db()
    c = db.cursor()
    x = "select * FROM "+ table + ";"
    c.execute(x)
    l = c.fetchall()
    return l

def select_sum(col, table, x, par):
    db = get_db()
    c = db.cursor()
    x = 'select sum('+col+') from '+table+' where '+x+'= \''+par+'\';'
    c.execute(x)
    l = c.fetchall()
    return l

def query_grants():
    db = get_db()
    c = db.cursor()
    c.execute('select title, submition_deadline from grants')
    l = c.fetchall()

    if not l:
        return "There are no grants at this time."
    else:
        return l

def select_where_null(col, table, x):
    db = get_db()
    c = db.cursor()
    x = 'select '+col+' from '+table+' where '+x+' is NULL;'
    c.execute(x)
    l = c.fetchall()
    return l

def join(col, table1, table2, x, y):
    db = get_db()
    c = db.cursor()
    x = 'select '+col+' from '+table1+' inner join '+table2+' ON '+table1+'.'+x+' = '+table2+'.'+y+';'
    c.execute(x)
    l = c.fetchall()
    return l

def join_where_null(col, table1, table2, x, y, z):
    db = get_db()
    c = db.cursor()
    x = 'select '+col+' from '+table1+' inner join '+table2+' on '+table1+'.'+x+' = '+table2+'.'+y+' where '+z+' is NULL;'
    c.execute(x)
    l = c.fetchall()
    return l
    
def join(col, table1, table2, x, y):
    db = get_db()
    c = db.cursor()
    x = 'select '+col+' from '+table1+' inner join '+table2+' on '+table1+'.'+x+' = '+table2+'.'+y+';'
    c.execute(x)
    l = c.fetchall()
    return l

'''
def update(sql, info):
        db = get_db()
        c = db.cursor()
        c.execute(sql, info)
        db.commit()

def update()
    db = get_db()
    c = db.cursor()
    x = 'update'+table+ ' set '+
'''
