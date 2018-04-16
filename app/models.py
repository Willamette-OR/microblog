from datetime import datetime
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import jwt
from flask_login import UserMixin


from app import app, db, login


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
                          key=app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_password_reset_token(token):
        """Verify a token and returns the user id if token is good"""

        try:
            user_id = jwt.decode(token, key=app.config['SECRET_KEY'],
                                 algorithms='HS256')['user_id']
        except:
            return

        return User.query.get(int(user_id))


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
