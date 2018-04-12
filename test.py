import unittest
from datetime import datetime, timedelta


from app import app, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):
    """Unit tests for the user data model"""

    def setUp(self):
        """Set up unit tests"""

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        """Clean up unit tests work space when stopping"""

        db.session.remove()
        db.drop_all()

    def test_password_hash(self):
        """Test user model's password methods"""

        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_following(self):
        """Test the follow and unfollow mechanism"""

        u1 = User(username='susan')
        u2 = User(username='john')
        db.session.add_all([u1, u2])
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followers.all(), [])

        u1.follow(u2)
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.first(), u2)
        self.assertEqual(u2.followers.first(), u1)

        u1.unfollow(u2)
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followers.all(), [])

    def test_followed_posts(self):
        """Test the followed posts query"""

        u1 = User(username='susan')
        u2 = User(username='john')
        u3 = User(username='tom')
        u4 = User(username='judy')
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        now = datetime.utcnow()
        p1 = Post(body='from tom', author=u3, timestamp=now)
        p2 = Post(body='from john', author=u2,
                  timestamp=now + timedelta(seconds=1))
        p3 = Post(body='from susan', author=u1,
                  timestamp=now + timedelta(seconds=2))
        p4 = Post(body='from tom', author=u3,
                  timestamp=now + timedelta(seconds=3))
        db.session.add_all([p1, p2, p3, p4])

        u1.follow(u2)
        u2.follow(u3)
        u3.follow(u4)
        u4.follow(u1)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed_posts().all(), [p3, p2])
        self.assertEqual(u2.followed_posts().all(), [p4, p2, p1])
        self.assertEqual(u3.followed_posts().all(), [p4, p1])
        self.assertEqual(u4.followed_posts().all(), [p3])


if __name__ == '__main__':
    unittest.main(verbosity=2)
