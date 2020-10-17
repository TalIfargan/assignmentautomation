from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app import db, login
from datetime import datetime
from flask_login import UserMixin
from time import time
import jwt


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    fullname = db.Column(db.String(100))
    student_number = db.Column(db.String(10), unique=True)
    password_hash = db.Column(db.String(128))
    covers = db.relationship('Cover', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
                          app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')()

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Cover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(10))
    course_name = db.Column(db.String(64))
    faculty = db.Column(db.String(100))
    partner_name = db.Column(db.String(100))
    partner_id = db.Column(db.String(9))
    year = db.Column(db.Integer)
    semester = db.Column(db.String(10))
    assignment_number = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    submission_date = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return self.course_name
