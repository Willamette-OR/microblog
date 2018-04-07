from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    """A class for user data model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(256))
    last_seen = db.Column(db.DateTime, default=None)


    def __repr__(self):
        """String representation for user objects"""

        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """Take the input password, create and save the password hash"""

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Take the input password and verify if it's the same as the saved"""

        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    """A class for post data model"""

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        """String representation for post objects"""

        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    """A user loader to be registered the login manager instance"""

    return User.query.get(int(id))
