# test_moderator.py
import unittest
from App.models import Moderator
from App.tests.test_base import BaseTestCase

class ModeratorTestCase(BaseTestCase):
    def test_new_moderator(self):
        mod = Moderator("robert", "robertpass")
        assert mod.username == "robert"

    def test_moderator_get_json(self):
        mod = Moderator("robert", "robertpass")
        self.assertDictEqual(mod.get_json(), {
            "id": None,
            "username": "robert",
            "competitions": []
        })

if __name__ == '__main__':
    unittest.main()
