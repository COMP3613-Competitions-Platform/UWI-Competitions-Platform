# test_student.py
import unittest
from App.models import Student
from App.tests.test_base import BaseTestCase

class StudentTestCase(BaseTestCase):
    def test_new_student(self):
        student = Student("dan", "jamespass")
        assert student.username == "dan"

    def test_student_get_json(self):
        student = Student("james", "jamespass")
        self.assertDictEqual(student.get_json(), {
            "id": None,
            "username": "james",
            "rating_score": 0,
            "comp_count": 0,
            "curr_rank": 0
        })

if __name__ == '__main__':
    unittest.main()
