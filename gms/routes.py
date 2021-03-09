from gms import app
import os
from datetime import datetime
from database import *
from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

ALLOWED_EXTENSIONS = set(['pdf', 'doc', 'docx'])

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, email, fname, lname, account):
        self.id = email
        self.first_name = fname
        self.last_name = lname
        self.account = account

user_db = {}

@login_manager.user_loader
def load_user(id):
    return user_db.get(id)

@login_manager.unauthorized_handler
def unauthorized():
    flash('Please login to view the page')
    return redirect(url_for('index'))

@app.route('/',methods=['GET','POST'])
def index():

    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    if request.method == "POST":
        if check_login(request.form['email']):
            user_info = select_where('*', 'account', 'email', request.form['email'])
            print(user_info)
            print(request.form['userclass'])
            valid_password = check_password_hash(user_info[0][1], request.form['password'])
            if valid_password and request.form['userclass'] == user_info[0][2]:
                acc_info = select_where('*', request.form['userclass'], 'email', request.form['email'])
                if request.form['userclass'] == 'admin':
                    user = User(user_info[0][0], acc_info[0][2], acc_info[0][3], user_info[0][1])
                    user_db[user_info[0][0]] = user
                    login_user(user)
                else:
                    user = User(user_info[0][0], acc_info[0][1], acc_info[0][2], user_info[0][1])
                    user_db[user_info[0][0]] = user
                    login_user(user)
                return redirect(url_for('homepage'))
            else:
                flash('wrong password')
        else:
            flash("That login does not exist")

    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        id_num = 0
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        account = request.form['userclass']

        print(account)

        sql = "INSERT into account values(?, ?, ?)"
        data = (email, password, account)
        insert(sql,data)

        if account == 'admin':
            admin_sql = "INSERT into admin values(?, ?, ?, ?)"
            admin_data = (id_num, email, fname, lname)
            insert(admin_sql, admin_data)
        elif account == 'reviewer':
            re_sql = "INSERT into reviewer values(?, ?, ?)"
            re_data = (email, fname, lname)
            insert(re_sql, re_data)
        elif account == 'researcher':
            gs_sql = "INSERT into researcher values(?, ?, ?)"
            gs_data = (email, fname, lname)
            insert(gs_sql, gs_data)

        flash('You have successfully registered!')

        return redirect(url_for('index'))
    else:
        return render_template('register.html')
@app.route('/homepage')
@login_required
def homepage():
    return render_template('homepage.html')

@app.route('/grantupload', methods=['GET', 'POST'])
def grant_upload():
    if request.method == 'POST':
        title = request.form['title']
        sponsor = request.form['sponsor']
        date = request.form['deadline']
        file = request.files['file_up']

        deadline = format_datetime(date)

        now = datetime.now()
        post_date = now.strftime("%Y-%m-%d %H:%M:%S")
        print(post_date)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['GRANT'], filename))
        #upload filename to db

        sql= "INSERT into grants(title, sponsor, requirements, post_date, submition_deadline, added_by) values(?, ?, ?, ?, ?, ?)"
        values =(title, sponsor, filename, post_date, deadline, "admin_id")
        insert(sql, values)
    return render_template('grant_upload.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/show')
def show():
    all = select_all('grants')
    print(all)
    return 'hello'
#this takes the deadline submition from adding a new grant
#and reformats it into a form appropiate for sql injection
#YYYY-MM-DD HH:MI:SS
def format_datetime(date):
    string = date.split(' ')
    day = string[0].split('/')
    fday = day[2]+'-'+day[0]+'-'+day[1]
    if string[2] == 'PM':
        time = string[1].split(':')
        num = int(time[0]) + 12
        time = str(num)+":"+time[1]+':00'
    else:
        time = string[1]+':00'
    final = fday+" "+time
    return final

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
