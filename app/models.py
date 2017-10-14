from flask_login import UserMixin

from . import db, bcrypt


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)

    def __init__(self, userID, password, email):
        self.userID = userID
        self.password = self.set_password(password)
        self.email = email

    def set_password(self, plaintext):
        return bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self.password, plaintext)

    def getUserName(self):
        return self.userID


class Photo(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imageName = db.Column(db.String(), unique=True, nullable=False)
    userID = db.Column(db.String(12), unique=True, nullable=False)
    path = db.Column(db.String(), unique=True, nullable=False)
    t1Path = db.Column(db.String(), unique=True, nullable=False)
    t2Path = db.Column(db.String(), unique=True, nullable=False)
    t3Path = db.Column(db.String(), unique=True, nullable=False)

    def __init__(self, imageName, userID, path, t1Path, t2Path, t3Path):
        self.imageName = imageName
        self.userID = userID
        self.path = path
        self.t1Path = t1Path
        self.t2Path = t2Path
        self.t3Path = t3Path