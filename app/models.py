from datetime import datetime
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import jwt
import os
from flask import current_app, url_for, send_from_directory
from flask_login import UserMixin


from app import db, login
from app.search import add_to_index, remove_from_index, query_index


follower = db.Table('follower',
                    db.Column('followed_id', db.Integer,
                              db.ForeignKey('user.id')),
                    db.Column('followers_id', db.Integer,
                              db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    """A class for user data model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(256))
    last_seen = db.Column(db.DateTime, default=None)
    photo_name = db.Column(db.String(120), default=None)
    followed = db.relationship('User', secondary=follower,
                               primaryjoin=(id == follower.c.followers_id),
                               secondaryjoin=(id == follower.c.followed_id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def __repr__(self):
        """String representation for user objects"""

        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """Take the input password, create and save the password hash"""

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Take the input password and verify if it's the same as the saved"""

        return check_password_hash(self.password_hash, password)

    def avatar(self, size=32):
        """Create the url for users' avatar images"""

        hex_d = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{0}?d=mm&s={1}'.format(hex_d,
                                                                       size)

    def uploaded_photo(self):
        """Return the uploaded photo"""

        if not self.photo_name:
            return

        # Pass a datetime query string to force browser to load new image
        return url_for('main.profile_photos', filename=self.photo_name,
                       timestamp=datetime.utcnow())

    def is_following(self, user):
        """Tell if self is following a given user"""

        return self.followed.filter_by(username=user.username).count() > 0

    def follow(self, user):
        """Follow a user if not already following"""

        if not self.is_following(user) and self.id != user.id:
            self.followed.append(user)

    def unfollow(self, user):
        """Unfollow a user if is currently following"""

        if self.is_following(user) and self.id != user.id:
            self.followed.remove(user)

    def followed_posts(self):
        """Return a query object with all followed users' posts and self's own
        posts"""

        followed = Post.query.join(
            follower, (Post.user_id == follower.c.followed_id)).filter(
                follower.c.followers_id == self.id)
        own = self.posts

        return followed.union(own).order_by(Post.timestamp.desc())

    def create_password_reset_token(self, expire=600):
        """Create a token for resetting user passwords"""

        return jwt.encode({'user_id': self.id, 'exp': time() + expire},
                          key=current_app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_password_reset_token(token):
        """Verify a token and returns the user id if token is good"""

        try:
            user_id = jwt.decode(token, key=current_app.config['SECRET_KEY'],
                                 algorithms='HS256')['user_id']
        except:
            return

        return User.query.get(int(user_id))


class SearchMixin(object):
    """A super class for Post with methods to sync between the SQLAlchemy
    database and the search engine database"""

    @classmethod
    def search(cls, expression, page, per_page):
        """Search expression and return objects"""

        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        """Save changed objects to the session"""

        session._changes = {
            'add': [obj for obj in session.new if isinstance(obj, cls)],
            'update': [obj for obj in session.dirty if isinstance(obj, cls)],
            'delete': [obj for obj in session.deleted if isinstance(obj, cls)]
        }

    @classmethod
    def after_commit(cls, session):
        """Update the search engine database after committing changes to the
        SQLAlchemy database"""

        for obj in session._changes['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['delete']:
            remove_from_index(cls.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        """Re-index all objects in the table"""

        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class Post(SearchMixin, db.Model):
    """A class for post data model"""

    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        """String representation for post objects"""

        return '<Post {}>'.format(self.body)


# Register event handlers for before and after commits
db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit)


@login.user_loader
def load_user(id):
    """A user loader to be registered the login manager instance"""

    return User.query.get(int(id))
