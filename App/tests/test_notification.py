
import unittest
from App.models import Notification
from App.tests.test_base import BaseTestCase


class NotificationTestCase(BaseTestCase):
    def test_new_notification(self):
        notification = Notification(1, "Ranking changed!")
        assert notification.student_id == 1 and notification.message == "Ranking changed!"

    def test_notification_get_json(self):
        notification = Notification(1, "Ranking changed!")
        self.assertDictEqual(notification.get_json(), {
            "id": None,
            "student_id": 1,
            "notification": "Ranking changed!"
        })


if __name__ == '__main__':
    unittest.main()