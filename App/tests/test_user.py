# test_user.py
import unittest
from werkzeug.security import generate_password_hash
from App.models import User
from App.tests.test_base import BaseTestCase

class UserTestCase(BaseTestCase):
    def test_new_user(self):
        user = User("ryan", "ryanpass")
        assert user.username == "ryan"

    def test_hashed_password(self):
        password = "ryanpass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("ryan", password)
        assert user.password != password

    def test_check_password(self):
        password = "ryanpass"
        user = User("ryan", password)
        assert user.check_password(password)

if __name__ == '__main__':
    unittest.main()
