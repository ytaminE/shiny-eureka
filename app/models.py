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

    def __repr__(self):
        return "<name %r email %r>" % (self.userID, self.email)

    def set_password(self, plaintext):
        return bcrypt.generate_password_hash(plaintext)

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self.password, plaintext)
        # return plaintext == self.password
