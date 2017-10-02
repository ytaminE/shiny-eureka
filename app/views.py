import os
import glob
import shutil

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from wand.image import Image

from . import app, db, login_manager
from .models import User

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


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
    user_id = current_user.get_id()
    img_path = app.config['UPLOAD_FOLDER'] + '/' + user_id + '/'

    all_image_list = [glob.glob(img_path + '*.%s' % ext) for ext in ALLOWED_EXTENSIONS]

    images = [item for image_list in all_image_list for item in image_list]

    images = [os.path.basename(x) for x in images]

    return render_template('home.html', images=images, user_id=user_id)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/empty', methods=['GET', 'POST'])
@login_required
def empty():
    if current_user.is_authenticated and request.method == 'POST':
        user_id = current_user.get_id()
        upload_path = app.config['UPLOAD_FOLDER'] + '/' + user_id
        shutil.rmtree(upload_path)
    return redirect('home')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.is_authenticated and request.method == 'POST':
        user_id = current_user.get_id()

        # check if the post request has the file part
        if 'uploadedfile' not in request.files:
            app.logger.info('NO FILE PART')
            flash('No file part')
            return redirect(request.url)
        file = request.files['uploadedfile']
        # if user does not select file, browser also submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Pass it a filename and it will return a secure version of it.
            # This filename can then safely be stored on a regular file system and passed to os.path.join().
            # The filename returned is an ASCII only string for maximum portability.
            filename = secure_filename(file.filename)

            save_path = app.config['UPLOAD_FOLDER'] + '/' + user_id + '/'
            resize_path = save_path + 'resize/'
            rotate_path = save_path + 'rotate/'
            enhance_path = save_path + 'enhancement/'

            if not os.path.exists(save_path):
                os.makedirs(save_path)
            if not os.path.exists(resize_path):
                os.makedirs(resize_path)
            if not os.path.exists(rotate_path):
                os.makedirs(rotate_path)
            if not os.path.exists(enhance_path):
                os.makedirs(enhance_path)

            file.save(os.path.join(save_path, filename))

            with Image(filename=save_path + filename) as img:
                with img.clone() as i:
                    i.resize(int(i.width * 0.2), int(i.height * 0.2))
                    i.save(filename=resize_path + filename)
                with img.clone() as i:
                    i.rotate(90)
                    i.save(filename=rotate_path + filename)
                with img.clone() as i:
                    i.evaluate(operator='rightshift', value=1, channel='blue')
                    i.save(filename=enhance_path + filename)

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
