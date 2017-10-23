import os
import glob
import shutil

from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from wand.image import Image

from . import app, db, login_manager, s3
from .models import User, Photo

# Restriction on image types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'JPG', 'PNG', 'JPEG', 'GIF'}


# Route for the welcome page
@app.route('/')
@app.route('/welcome')
def welcome():
    if current_user.is_authenticated:
        return redirect('home')
    else:
        return render_template('welcome.html')


# Route for the home page (used for showing pictures)
@app.route('/home')
@login_required
def home():
    user_id = current_user.get_id()

    # img_path = app.config['UPLOAD_FOLDER'] + '/' + user_id + '/'
    # all_image_list = [glob.glob(img_path + '*.%s' % ext) for ext in ALLOWED_EXTENSIONS]
    # images = [item for image_list in all_image_list for item in image_list]
    # images = [os.path.basename(x) for x in images]

    bucket = s3.Bucket(app.config['IMAGE_BUCKET_NAME'])
    images = [obj.key.split('/')[-1] for obj in bucket.objects.filter(Prefix=user_id + '/original/')]
    return render_template('home.html', bucket_name = app.config['IMAGE_BUCKET_NAME'], images=images, user_id=user_id)


# Route for empty images action
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
        if os.path.exists(upload_path):
            shutil.rmtree(upload_path)

        # Delete images in S3
        bucket = s3.Bucket(app.config['IMAGE_BUCKET_NAME'])
        for obj in bucket.objects.filter(Prefix = user_id + '/'):
            s3.Object(bucket.name, obj.key).delete()

    return redirect('home')


# Route for upload function
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

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            processAndStoreImage(file, username, user_id)
            return redirect(url_for('home'))

    return redirect('home')


# Route for handling the login page logic
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


# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('welcome.html')


# Route for register page
@app.route('/register')
def register():
    return render_template('register.html')


# Route for register submit
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


# TA test page
@app.route('/uploadForm', methods=['GET', 'POST'])
def uploadForm():
    return render_template('uploadForm.html')


# Used for TA test
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
            # If user does not select file, browser also submit a empty part without filename
            if file.filename == '':
                return redirect(request.url)
            if file and allowed_file(file.filename):
                processAndStoreImage(file, username, user_id)
                return redirect(url_for('uploadForm'))
        else:
            error = 'Username or password is incorrect. Please try again.'
    return render_template('uploadForm.html', error=error)


# Process the original image and save the image with its transformations
def processAndStoreImage(file, username, user_id):
    # Pass it a filename and it will return a secure version of it.
    # This filename can then safely be stored on a regular file system and passed to os.path.join().
    # The filename returned is an ASCII only string for maximum portability.
    filename = secure_filename(file.filename)
    save_path = app.config['UPLOAD_FOLDER'] + '/' + user_id + '/'
    s3_save_path = user_id + '/'

    s3_t1_path = s3_save_path + 'resize/'
    s3_t2_path = s3_save_path + 'rotate/'
    s3_t3_path = s3_save_path + 'enhancement/'

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
    # Save the original image into the server
    file.save(os.path.join(save_path, filename))
    # s3.upload_fileobj(file, app.config['IMAGE_BUCKET_NAME'], s3_save_path+file.filename)
    s3.Object(app.config['IMAGE_BUCKET_NAME'], s3_save_path + 'original/'+ filename).put(Body = open(save_path+filename, 'rb'))
    with Image(filename=save_path + filename) as img:
        # First transformation
        with img.clone() as i:
            i.resize(int(i.width * 0.7), int(i.height * 0.7))
            i.save(filename=t1_path + filename)
            # s3.upload_fileobj(FileStorage(open(t1_path+filename,'rb')), app.config['IMAGE_BUCKET_NAME'], s3_t1_path + filename)
            # s3.Bucket(app.config['IMAGE_BUCKET_NAME']).put_object(s3_t1_path + filename,FileStorage(open(t1_path+filename,'rb')))
            s3.Object(app.config['IMAGE_BUCKET_NAME'], s3_t1_path + filename).put(Body= open(t1_path+filename,'rb'))

        # Second transformation
        with img.clone() as i:
            i.rotate(90)
            i.save(filename=t2_path + filename)
            # s3.upload_fileobj(FileStorage(open(t1_path+filename,'rb')), app.config['IMAGE_BUCKET_NAME'], s3_t2_path + filename)
            # s3.Bucket(app.config['IMAGE_BUCKET_NAME']).put_object(s3_t2_path + filename,
            #                                                       FileStorage(open(t2_path + filename, 'rb')))
            s3.Object(app.config['IMAGE_BUCKET_NAME'], s3_t2_path + filename).put(Body=open(t2_path+filename,'rb'))

        # Third transformation
        with img.clone() as i:
            i.evaluate(operator='rightshift', value=1, channel='red')
            i.save(filename=t3_path + filename)
            # s3.upload_fileobj(FileStorage(open(t1_path+filename,'rb')), app.config['IMAGE_BUCKET_NAME'], s3_t3_path + filename)
            # s3.Bucket(app.config['IMAGE_BUCKET_NAME']).put_object(s3_t3_path + filename,
            #                                                       FileStorage(open(t3_path + filename, 'rb')))
            s3.Object(app.config['IMAGE_BUCKET_NAME'], s3_t3_path + filename).put(Body=open(t3_path+filename,'rb'))

    # Store the path information into the database
    image = Photo(filename, username, save_path, t1_path, t2_path, t3_path)
    db.session.add(image)
    db.session.commit()

    #TODO: Delete the images stored in the server


# A helper function used to add restriction on file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
