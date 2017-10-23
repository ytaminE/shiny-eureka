import boto3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__, instance_relative_config=True)

# Load the default configuration
app.config.from_object('config')

# Load the configuration from the instance folder
app.config.from_pyfile('development.py')

# Load the file specified by the APP_CONFIG_FILE environment variable
# Variables defined here will override those in the default configuration
app.config.from_envvar('APP_CONFIG_FILE')

app.config['UPLOAD_FOLDER'] = 'app/static/img/upload'

# MySQL Database
db = SQLAlchemy(app)

# AWS S3
# AWS_ACCESS_KEY_ID = 'AKIAJ7SCE2KPKMDN2L2Q'
# AWS_SECRET_ACCESS_KEY = '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'

# s3 = boto3.client(
#     's3',
#     aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
#     aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
# )

s3 = boto3.resource('s3')
# for bucket in s3.buckets.all():
#     print(bucket.name)


# Flask-Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Flask Bcrypt
bcrypt = Bcrypt(app)

from app import views