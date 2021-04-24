from gms import app, mail
import os
import pdfkit
import csv
import io
from datetime import datetime
from database import *
from flask import render_template, request, redirect, url_for, flash, send_from_directory, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from threading import Thread
from flask_mail import Message

#allowed extensions for grant file upload
ALLOWED_EXTENSIONS = set(['pdf', 'doc', 'docx'])

#login manager for flask_login and related functions
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

#main page, hanldes login
@app.route('/',methods=['GET','POST'])
def index():

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        if check_login(request.form['email']):
            user_info = select_where('*', 'account', 'email', request.form['email'])
            print(user_info)
            valid_password = check_password_hash(user_info[0][1], request.form['password'])
            if valid_password and request.form['userclass'] == user_info[0][2]:
                acc_info = select_where('*', request.form['userclass'], 'email', request.form['email'])
                if request.form['userclass'] == 'admin':
                    user = User(user_info[0][0], acc_info[0][2], acc_info[0][3], user_info[0][2])
                    user_db[user_info[0][0]] = user
                    login_user(user)
                else:
                    user = User(user_info[0][0], acc_info[0][1], acc_info[0][2], user_info[0][2])
                    user_db[user_info[0][0]] = user
                    login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong Password or Account Type')
        else:
            flash("That login does not exist")

    return render_template('index.html')

#registration
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        #system has only one administator, so we just set the id here
        try:
            id_num = request.form['num']
        except:
            print('no id num')
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        dept = request.form['dept']
        account = request.form['userclass']

        sql = "INSERT into account values(?, ?, ?)"
        data = (email, password, account)
        insert(sql,data)

        if account == 'admin':
            admin_sql = "INSERT into admin values(?, ?, ?, ?, ?)"
            admin_data = (id_num, email, fname, lname, dept)
            insert(admin_sql, admin_data)
        elif account == 'reviewer':
            re_sql = "INSERT into reviewer values(?, ?, ?, ?)"
            re_data = (email, fname, lname, dept)
            insert(re_sql, re_data)
        elif account == 'researcher':
            #get user specific field values here to avoid error
            #dept and status should return null if nothin is entered
            status = request.form['status']
            gs_sql = "INSERT into researcher values(?, ?, ?, ?, ?)"
            gs_data = (email, fname, lname, dept, status)
            insert(gs_sql, gs_data)

        #send email confirmation to the user that they've created their account
        send_mail('Grant MS Registration', email, render_template('reg_email.txt', fname=fname, lname=lname, email=email, dept=dept, account=account))

        flash('You have successfully registered!')

        return redirect(url_for('index'))
    else:
        return render_template('register.html')

#main dashboard route, sends user to different template depending on user class
#gathers info from database to be displayed on template
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    usertype = current_user.account
    if usertype == 'admin':
        assign = select_where_null('*', 'proposals', 'assigned_reviewer')
        grant = join_where_null('*', 'proposals', 'grants', 'grant_id', 'id', 'proposals.assigned_reviewer')
        pending = select_where('*', 'proposals', 'approved', 'NULL')
        test = select_all("proposals")
        reviewer = select_all('reviewer')
        approval = join('*', 'proposals', 'reports', 'id', 'proposal_id')
        re_info = select_all('report_info')
        total = select_where('*', 'proposals', 'approved', '1')
        gt = select_sum('funding_re', 'proposals', 'approved', '1')
        print(grant)

        return render_template('admindash.html', assign=assign, pending=approval, grant=grant, reviewer=reviewer, re_info=re_info, total=total, gt=gt)

    elif usertype == 'researcher':
        grant = select_all("grants")
        pending = join_where_null('*', 'proposals', 'researcher', 'submitted_by','email','proposals.approved')        
        done = select_all('proposals')
        return render_template('gsdash.html', grant=grant, pending=pending, done=done, id=current_user.id)

    elif usertype == 'reviewer':
        assign = select_where('*', 'proposals', 'assigned_reviewer', current_user.id)
        pending = join('*', 'proposals', 'reports', 'id', 'proposal_id')
        print(pending)

        return render_template('reviewerdash.html', assign=assign, pending=pending)

#grants page, visible by all users. only admin can post grants, and
#only grant seeker can apply
@app.route('/grants', methods=['GET','POST'])
def grants():
    grants = select_all('grants')

    return render_template('admingrants.html', grants=grants)

#display page for displaying the requirements of a specific grant
#shows off the requirements file uploaded during grant creation
@app.route('/grants/<grantid>', methods=['GET'])
def showGrant(grantid):

    #ONLY PDF WILL BE SHOWN IN IFRAME
    #uploading a .docx file will cause it to download (chrome)
    grant = select_where('*', 'grants', 'id', grantid)
    floc = url_for('static', filename="grants/"+grant[0][4])
    pro_app = url_for('proposal_upload', test=grantid)

    return render_template('showgrants.html', pro_app=pro_app, loc=floc)

#only for admin, the form to post a new grant
@app.route('/grantupload', methods=['GET', 'POST'])
@login_required
def grant_upload():
    if request.method == 'POST':
        title = request.form['title']
        sponsor = request.form['sponsor']
        fund = request.form['fund']
        date = request.form['deadline']
        file = request.files['file']
        dept = request.form['dept']

        if date == "":
            flash("Please enter a valid date.")
        elif title == "" or sponsor == "":
            flash("The Title or Sponsor was left blank")
        else:
            deadline = format_datetime(date)
            now = datetime.now()
            post_date = now.strftime("%Y-%m-%d %H:%M:%S")

           #upload filename to db
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['GRANT'], filename))
            sql= "INSERT into grants(title, fund, sponsor, requirements, post_date, submition_deadline, added_by, dept) values(?, ?, ?, ?, ?, ?, ?, ?)"
            values=(title, fund, sponsor, filename, post_date, deadline, "admin_id", dept)
            insert(sql, values)
            flash("The grant has been uploaded")

        else:
            flash('Upload the file requirements')

        #Send email to grant seekers to notify them of the new grant that has been posted
        db = get_db()
        c = db.cursor()
        c.execute('SELECT * FROM researcher')
        researchers = c.fetchall()
        for email in researchers:
            send_mail("New Grant Posted!", email[0], render_template("new_prop.txt", dept=dept, title=title, fund=fund, sponsor=sponsor, deadline=deadline))
           

    return render_template('grant_upload.html')

#route for uploading a proposal to a grant, supplies template with tag list from db
@app.route('/proposalupload/<test>', methods=['GET'])
def proposal_upload(test):

    taglist = select_all('tags')
    return render_template('proposal_upload.html', id=test, taglist=taglist)

#logic for processing proposal submission, a few different things going on here
@app.route('/proposalsubmit', methods=['POST'])
def pro_submit():

    if request.method == 'POST':
        #getting all data from form
        print(request.form)
        name = request.form['name']
        status = request.form['ftpt']
        dept = request.form['department']
        email = request.form['email']
        amount = request.form['request']
        id = request.form['grant']
        budget_items = request.form.getlist('budget')

        title = request.form['title']
        summary = request.form['summary']
        workplan = request.form['workplan']
        significance = request.form['significance']
        outcome = request.form['outcome']

        taglist = request.form.getlist('selected')

        now = datetime.now()
        post_date = now.strftime("%Y-%m-%d %H:%M:%S")

        #updating proposal info
        sql = "INSERT into proposals(title, summary, workplan, significance, outcome, funding_re, grant_id, date_submitted, submitted_by) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = (title, summary, workplan, significance, outcome, amount, id, post_date, email)

        insert(sql, values)

        #getting new proposal ID
        db = get_db()
        c = db.cursor()
        c.execute('SELECT last_insert_rowid();')
        l = c.fetchall()
        proposal_id = l[0][0]

        #updating budget items
        budgetT = ''
        while len(budget_items) != 0:
            item = budget_items.pop(0)
            cost = budget_items.pop(0)
            justification = budget_items.pop(0)

            budget_sql = "INSERT INTO budget(item, cost, justification, proposal_id) VALUES(?, ?, ?, ?)"
            values = (item, cost, justification, proposal_id)
            budgetT += "<tr><td>"+item+"</td><td>"+cost+"</td><td>"+justification+"</td></tr>"
            insert(budget_sql, values)

        #updating tag/proposal
        tagString = ''
        for tag in taglist:
            tag_sql = "INSERT INTO tagged_proposals(tag, proposal_id) VALUES(?, ?)"
            values = (tag, proposal_id)
            insert(tag_sql, values)

            tagString += tag+", "

        # generating and saving pdf
        conf = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        pdfkit.from_string("<h1>"+title+"</h1>" + \
                "<h1>Requested Funding: $"+amount+"</h1>" + \
                "<table><tr><td>Applicant Name: "+name+"</td></tr><tr><td>Department: "+dept+" - "+status+"</td></tr><tr><td>Email Contact: "+email+"</td></tr></table><br>" + \
                "Tags: "+tagString+"<br>" + \
                "<h3>Summary:</h3><p>"+summary+"</p><br>" + \
                "<h3>Workplan</h3><p>"+workplan+"</p><br>" + \
                "<h3>Significance:</h3><p>"+significance+"</p><br>" + \
                "<h3>Outcome:</h3><p>"+outcome+"</p><br>" + \
                "<h3>Budget</h3><table><tr><th>Budget Item</th><th>Cost</th><th>Justification</th></tr>"+budgetT+"</table>",
                "gms/static/proposals/"+str(proposal_id)+".pdf", configuration=conf)

        flash('WEll DONE')
    
    #sending email notification 
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM admin')
    admin = c.fetchall()
    for a in admin:
        send_mail("New proposal has posted!", a[1], render_template("prop_notif.txt", name=name, email=email, id=id))
                
    return redirect(url_for('proposal_upload', test=id))

#page for assigning reviewers, only visible by admin
@app.route('/assignment', methods=['POST'])
def assign():

    if request.method == 'POST':
        email = request.form['remail']
        seperate = email.split(" ")
        email = seperate[0]
        pid = seperate[1]
        now = datetime.now()
        assigned = now.strftime("%Y-%m-%d %H:%M:%S")

        #make sure reviewer exists
        exists = check_login(email)
        if exists:

            sql = 'UPDATE proposals SET assigned_reviewer=\''+email+'\', date_assigned=\''+assigned+'\' WHERE id=\''+pid+'\';'
            values = (email, assigned, pid)
            sql_script(sql)

            rsql = 'Insert into reports(proposal_id, reviewer, assigned_by) values(?,?,?)'
            info = (pid, email, current_user.id)
            insert(rsql, info)

            #send an email notification to reviewer
            send_mail('You have a new proposal assignment!', email, render_template("prop_assigned.txt", email=email, admin=current_user.id, pid=pid))
            
            flash('Reviewer Assigned')

        else:
            flash('Reviewer specified does not exist')
    return redirect(url_for('dashboard'))

#only for admin, processes a grant decision
@app.route('/decision/<pro_id>', methods=['POST'])
def decide(pro_id):

    if request.method == 'POST':
        if request.form['decide'] == 'accept':
            sql = 'UPDATE proposals SET approved=1 WHERE id=\''+pro_id+'\';'
            sql_script(sql)
            #get the admin id number to add to proposal table
            sql = "UPDATE proposals SET approved_by="

        elif request.form['decide'] == 'decline':
            sql = 'UPDATE proposals SET approved=0 WHERE id=\''+pro_id+'\';'
            sql_script(sql)
            #get the admin id number to add to proposal table
            sql = "UPDATE proposals SET approved_by="

        #send notification to the researcher that their proposal has completed review
        db = get_db()
        c = db.cursor()
        c.execute('SELECT * FROM proposals where id=?', [pro_id])
        prop = c.fetchall()
        for p in prop:
            send_mail("Decision on your proposal is ready", p[12], render_template("prop_reviewed.txt",title=p[1]))

    return redirect(url_for('dashboard'))

#account settings page, visible for all accounts
@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    usertype = current_user.account
    ini_email = current_user.id
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']

        if usertype == 'admin':
            sql = 'UPDATE admin SET email=?, name=?, lastname=? WHERE email=?'
            values = (email, fname, lname, ini_email)
            insert(sql, values)

            asql = 'UPDATE account SET email=? where email=?'
            avalues = (email, ini_email)
            insert(asql, avalues)

        elif usertype == 'reviewer':
            sql = 'UPDATE reviewer SET email=?, name=?, lastname=? WHERE email=?'
            values = (email, fname, lname, ini_email)
            insert(sql, values)

            asql = 'UPDATE account SET email=? where email=?'
            avalues = (email, ini_email)
            insert(asql, avalues)

        elif usertype == 'researcher':
            sql = 'UPDATE researcher SET email=?, name=?, lastname=? WHERE email=?'
            values = (email, fname, lname, ini_email)
            insert(sql, values)

            asql = 'UPDATE account SET email=? where email=?'
            avalues = (email, ini_email)
            insert(asql, avalues)

        #Send email notification to user about account changes
        send_mail('Your Account Information Was Changed', current_user.id, render_template('acct_change.txt', fname=fname, lname=lname))
        
        flash('Your account has been updated.', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        if usertype == 'admin':
            account = select_where('*', 'admin', 'email', ini_email)

        elif usertype == 'reviewer':
            account = select_where('*', 'reviewer', 'email', ini_email)

        elif usertype == 'researcher':
            account = select_where('*', 'researcher', 'email', ini_email)

    return render_template('account_page.html', account=account)

#proposal review page, only visible by assigned reviewer
@app.route('/review/<pro_id>', methods=['GET', 'POST'])
@login_required
def pro_review(pro_id):

    valid = select_where('assigned_reviewer', 'proposals', 'id', pro_id)
    valid_check = valid[0][0]
    print(valid)
    print(valid_check)

    #serves proposal pdf file when user clicks the download button
    if request.method == 'POST':
        f = pro_id + '.pdf'
        path = os.path.join('static/proposals/')
        return send_file(path + f)

    #checks if user is allowed to view proposal
    if current_user.account == 'reviewer' and valid_check == current_user.id:
        return render_template('pro_review.html', pro_id = pro_id)
    else:
        return redirect(url_for('dashboard'))

#processing of review
@app.route('/re_submit', methods=['POST'])
def review_submit():

    if request.method == 'POST':
        pro_id = request.form['pro_id']
        sig = request.form['sig']
        work = request.form['work']
        outcomes = request.form['outcomes']
        budget = request.form['budget']
        comments = request.form['comments']
        now = datetime.now()
        reviewed = now.strftime("%d-%b-%Y %H:%M:%S")
        complete = 1

        sql = 'SELECT id FROM reports where proposal_id =\''+ pro_id +'\' and reviewer = \'' +current_user.id+'\';'
        id = sql_script(sql)
        usql = 'UPDATE reports SET rev_reviewed=\''+reviewed+'\' WHERE proposal_id=\''+pro_id+'\';'
        sql_script(usql)

        sql= 'INSERT into report_info(id, signifigance, work_plan, outcomes, budget_proposal, comments) values(?, ?, ?, ?, ?, ?)'
        values = (pro_id, sig, work, outcomes, budget, comments)
        insert(sql, values)

        sql = 'UPDATE reports set completed = 1 where proposal_id =\''+ pro_id +'\';'
        print(sql)
        sql_script(sql)

    #Send admin a notif that a reviewer completed their review
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM admin')
    admin = c.fetchall()
    rev_name = current_user.first_name
    for a in admin:
        send_mail("Reviewer completed their assignment", a[1], render_template("rev_completed.txt", aname=a[2], pro_id=pro_id, rev_name=rev_name))

    return redirect(url_for('dashboard'))

#generates report for a grant
@app.route('/grant_report/<r_type>/<grant_id>', methods=['GET'])
def grant_report(r_type, grant_id):

    if r_type == 'Summary':
        #get information about the grant from db
        grantInfo = join('*', 'proposals', 'grants', 'grant_id', 'id')

        accepted = []
        denied = []
        pending = []

        award = 0

        for grant in grantInfo:
            if (grant[7] == int(grant_id)):
                #determine status
                if grant[10] == 1:
                    accepted.append(grant)
                    award += grant[6]
                elif grant[10] == 0:
                    denied.append(grant)
                else:
                    pending.append(grant)

        title = grantInfo[(int(grant_id) - 1)][15]

        pdfstring = '<h1>'+title+" - "+r_type+' Report</h1><br>' + \
            '<h3>Accepted - ' + str(len(accepted)) + ', Denied - ' + str(len(denied)) + ', Pending - ' + str(len(pending)) + '</h3><br>' + \
            '<h3>Awarded Funding - ' + str(award) + '</h3>' + \
            '<h3>Accepted Proposals</h3><br>'
        
        if len(accepted) == 0:
            pdfstring += "<p>No proposals accepted at this time</p>"
        else:
            pdfstring += "<table><tr><th>Name</th><th>Proposal Title</th><th>Awarded Funding</th><th>Reviewer</th></tr>"
            for a in accepted:
                pdfstring += "<tr><td>"+a[12]+"</td><td>"+a[1]+"</td><td>"+str(a[6])+'</td><td>'+a[13]+"</td></tr>"
            pdfstring += "</table>"
        
        pdfstring += '<h3>Denied Proposals</h3>'

        if len(denied) == 0:
            pdfstring += "No proposals denied at this time"
        else:
            pdfstring += "<table><tr><th>Name</th><th>Proposal Title</th><th>Funding</th><th>Reviewer</th></tr>"
            for d in denied:
                pdfstring += "<tr><td>"+d[12]+"</td><td>"+d[1]+"</td><td>"+str(d[6])+'</td><td>'+d[13]+"</td></tr>"
            pdfstring += "</table>"
        
        pdfstring += '<h3>Pending Proposals</h3>'

        if len(pending) == 0:
            pdfstring += "No proposals pending at this time"
        else:
            pdfstring += "<table><tr><th>Name</th><th>Proposal Title</th><th>Funding</th><th>Reviewer</th></tr>"
            for p in pending:
                if p[13]:
                    pdfstring += "<tr><td>"+p[12]+"</td><td>"+p[1]+"</td><td>"+str(p[6])+'</td><td>'+p[13]+"</td></tr>"
                else:
                    pdfstring += "<tr><td>"+p[12]+"</td><td>"+p[1]+"</td><td>"+str(p[6])+'</td><td>No Reviewer Assigned</td></tr>'
            pdfstring += "</table>"    

        #cant figure out to how download this, will fix later
        conf = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        css = 'gms/static/styles/pdf.css'
        pdfkit.from_string(pdfstring, "gms/static/grant_reports/"+str(grant_id)+".pdf", configuration=conf, css=css)

        f = grant_id + '.pdf'
        path = os.path.join('static/grant_reports/')
        return send_file(path + f)
    
    elif r_type == 'Budget':
        #get information about the grant from db
        title = select_where('title', 'grants', 'id', grant_id)
        budget = join('*', 'proposals', 'budget', 'id', 'proposal_id')

        print(budget)

        accepted = []
        denied = []
        pending = []

        award = 0

        for b in budget:
            if (b[7] == int(grant_id)):
                #determine status
                if b[10] == 1:
                    accepted.append(b)
                    award += int(b[16])
                elif b[10] == 0:
                    denied.append(b)
                else:
                    pending.append(b)

        pdfstring = '<h1>'+title[0][0]+" - "+r_type+' Report</h1><br>' + \
            '<h3>Accepted Items - ' + str(len(accepted)) + ', Denied Items - ' + str(len(denied)) + ', Pending Items - ' + str(len(pending)) + '</h3><br>' + \
            '<h3>Awarded Funding - ' + str(award) + '</h3>' + \
            '<h3>Accepted Proposal Budgets</h3><br>'
        
        if len(accepted) == 0:
            pdfstring += "<p>No proposals accepted at this time</p>"
        else:
            pdfstring += "<table><tr><th>Name</th><th>Proposal Title</th><th>Budget Item Name</th><th>Cost</th><th>Justification</th></tr>"
            for a in accepted:
                pdfstring += "<tr><td>"+a[12]+"</td><td>"+a[1]+"</td><td>"+str(a[15])+'</td><td>'+str(a[16])+"</td><td>"+a[17]+"</tr>"
            pdfstring += "</table>"
        
        pdfstring += '<h3>Denied Proposal Budgets</h3>'

        if len(denied) == 0:
            pdfstring += "No proposals denied at this time"
        else:
            pdfstring += "<table><tr><th>Name</th><th>Proposal Title</th><th>Budget Item Name</th><th>Cost</th><th>Justification</th></tr>"
            for d in denied:
                pdfstring += "<tr><td>"+d[12]+"</td><td>"+d[1]+"</td><td>"+str(d[15])+'</td><td>'+str(d[16])+"</td><td>"+d[17]+"</tr>"
            pdfstring += "</table>"
        
        pdfstring += '<h3>Pending Proposal Budgets</h3>'

        if len(pending) == 0:
            pdfstring += "No proposals pending at this time"
        else:
            pdfstring += "<table style='border: 1px solid black;'><tr><th>Name</th><th>Proposal Title</th><th>Budget Item Name</th><th>Cost</th><th>Justification</th></tr>"
            for p in pending:
                pdfstring += "<tr><td>"+p[12]+"</td><td>"+p[1]+"</td><td>"+str(p[15])+'</td><td>'+str(p[16])+"</td><td>"+p[17]+"</tr>"
            pdfstring += "</table>"    

        #cant figure out to how download this, will fix later
        conf = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        css = 'gms/static/styles/pdf.css'
        pdfkit.from_string(pdfstring, "gms/static/grant_reports/"+str(grant_id)+".pdf", configuration=conf, css=css)

        f = grant_id + '.pdf'
        path = os.path.join('static/grant_reports/')
        return send_file(path + f)

#logs user out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#quickly view a table for debugging
@app.route('/show/<table>')
def show(table):
    print(table)
    all = select_all(table)
    print(all)
    return 'hello'

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

#Email Notification
def send_mail(subject, recipients, text_body):
    msg = Message(subject, recipients=[recipients])
    msg.body = text_body
    Thread(target=send_async_email, args=(app, msg)).start()



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

#checks uploaded file (for admin grant upload)
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
