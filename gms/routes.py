from gms import app
from database import *
from flask import render_template, request, redirect, url_for, flash

@app.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = request.form['password']

        sql = "INSERT into account values(?, ?, ?, ?)"
        data = (email, password, fname, lname)
        insert(sql,data)

        flash('You have successfully registered!')

        return redirect(url_for('index'))
    else:
        return render_template('register.html')
