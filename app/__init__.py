import boto3
import urllib.request

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
# app.config.from_envvar('APP_CONFIG_FILE')

app.config['UPLOAD_FOLDER'] = 'app/static/img/upload'

# MySQL Database
db = SQLAlchemy(app)

s3 = boto3.resource('s3',
                    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])

elb = boto3.client('elbv2',
                   aws_access_key_id = app.config['AWS_ACCESS_KEY_ID'],
                   aws_secret_access_key = app.config['AWS_SECRET_ACCESS_KEY'],
                   region_name = 'us-east-1')

instanceid = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read().decode()


# Flask-Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Flask Bcrypt
bcrypt = Bcrypt(app)


response = elb.register_targets(
    TargetGroupArn=
    'arn:aws:elasticloadbalancing:us-east-1:611618355222:targetgroup/userUI-group/30bfb86689697b01',
    Targets=[
        {
            'Id': instanceid,
            'Port':5000
        },
    ]
)

from app import views