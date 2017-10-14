import os
import glob
import shutil

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from wand.image import Image

from . import app, db, login_manager
from .models import User, Photo

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'JPG', 'PNG', 'JPEG', 'GIF'}


@app.route('/')
@app.route('/welcome')
def welcome():
    if current_user.is_authenticated:
        return redirect('home')
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
        username = current_user.getUserName()
        upload_path = app.config['UPLOAD_FOLDER'] + '/' + user_id
        images = Photo.query.filter_by(userID=username)
        for image in images:
            db.session.delete(image)
        db.session.commit()
        # Delete all the pictures under the upload_path
        shutil.rmtree(upload_path)

    return redirect('home')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.is_authenticated and request.method == 'POST':
        user_id = current_user.get_id()
        username = current_user.getUserName()

        # check if the post request has the file part
        if 'uploadedfile' not in request.files:
            app.logger.info('NO FILE PART')
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
            t1_path = save_path + 'resize/'
            t2_path = save_path + 'rotate/'
            t3_path = save_path + 'enhancement/'

            if not os.path.exists(save_path):
                os.makedirs(save_path)
            if not os.path.exists(t1_path):
                os.makedirs(t1_path)
            if not os.path.exists(t2_path):
                os.makedirs(t2_path)
            if not os.path.exists(t3_path):
                os.makedirs(t3_path)

            file.save(os.path.join(save_path, filename))

            with Image(filename=save_path + filename) as img:
                with img.clone() as i:
                    i.resize(int(i.width * 0.7), int(i.height * 0.7))
                    i.save(filename=t1_path + filename)
                with img.clone() as i:
                    i.rotate(90)
                    i.save(filename=t2_path + filename)
                with img.clone() as i:
                    i.evaluate(operator='rightshift', value=1, channel='red')
                    i.save(filename=t3_path + filename)

            image = Photo(filename, username, save_path, t1_path, t2_path, t3_path)
            db.session.add(image)
            db.session.commit()
            # return redirect(url_for('uploaded_file',filename=filename))
            return redirect(url_for('home'))

    return redirect('home')


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
    return render_template('welcome.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register_submit', methods=['GET', 'POST'])
def register_submit():
    error = 'Username already registered'
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(userID=username).first()
        if not user:
            password = request.form['password']
            email = request.form['email']
            user = User(username, password, email)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/uploadForm', methods=['GET', 'POST'])
def uploadForm():
    return render_template('uploadForm.html')


@app.route('/test/FileUpload', methods=['POST'])
def test_upload():
    error = None
    if request.method == 'POST':
        username = request.form['userID']
        password = request.form['password']
        file = request.files['uploadedfile']
        user = User.query.filter_by(userID=username).first()
        if user is not None and user.is_correct_password(password):
            login_user(user)
            user_id = current_user.get_id()
            if file.filename == '':
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = app.config['UPLOAD_FOLDER'] + '/' + user_id + '/'
                t1_path = save_path + 'resize/'
                t2_path = save_path + 'rotate/'
                t3_path = save_path + 'enhancement/'

                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                if not os.path.exists(t1_path):
                    os.makedirs(t1_path)
                if not os.path.exists(t2_path):
                    os.makedirs(t2_path)
                if not os.path.exists(t3_path):
                    os.makedirs(t3_path)

                file.save(os.path.join(save_path, filename))
                with Image(filename=save_path + filename) as img:
                    with img.clone() as i:
                        i.resize(int(i.width * 0.7), int(i.height * 0.7))
                        i.save(filename=t1_path + filename)
                    with img.clone() as i:
                        i.rotate(90)
                        i.save(filename=t2_path + filename)
                    with img.clone() as i:
                        i.evaluate(operator='rightshift', value=1, channel='red')
                        i.save(filename=t3_path + filename)
                image = Photo(filename, username, save_path, t1_path, t2_path, t3_path)
                db.session.add(image)
                db.session.commit()
                return redirect(url_for('uploadForm'))
        else:
            error = 'Username or password is incorrect. Please try again.'
    return render_template('uploadForm.html', error=error)

# # routes for testing database
# @app.route('/testdb')
# def testdb():
#     try:
#         print("----------------------")
#         for user in User.query.all():
#             print(user)
#         # db.session.query("1").from_statement("SELECT 1").all()
#         print("----------------------")
#         return '<h1>It works.</h1>'
#     except:
#         raise
#         return '<h1>Something is broken.</h1>'
