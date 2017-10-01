from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

from . import app, db, login_manager
from .models import User

import os

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route('/')
@app.route('/welcome')
def welcome():
    if current_user.is_authenticated:
        return render_template('home.html')
    else:
        return render_template('welcome.html')  # render a template


@app.route('/home')
@login_required
def home():
    return render_template('home.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'uploadedfile' not in request.files:
            app.logger.info('NO FILE PART')
            flash('No file part')
            return redirect(request.url)
        file = request.files['uploadedfile']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',filename=filename))
            return redirect(url_for('home'))

    return render_template('home.html')

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(userID=username).first()
        if user is not None and user.is_correct_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            error = 'Username or password is incorrect. Please try again.'

    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successfully')
    return render_template('welcome.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register_submit', methods=['GET', 'POST'])
def register_submit():
    error = 'Failed to register'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user = User(username, password, email)
        db.session.add(user)
        db.session.commit()
        flash("Register successfully")
        return redirect(url_for('login'))
    return render_template('register.html', error=error)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# routes for testing database
@app.route('/testdb')
def testdb():
    try:
        print("----------------------")
        for user in User.query.all():
            print(user)
        # db.session.query("1").from_statement("SELECT 1").all()
        print("----------------------")
        return '<h1>It works.</h1>'
    except:
        raise
        return '<h1>Something is broken.</h1>'
