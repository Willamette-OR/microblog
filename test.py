import unittest
from app import app, db
from app.models import User


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
