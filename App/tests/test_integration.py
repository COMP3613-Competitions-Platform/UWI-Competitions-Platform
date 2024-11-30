from App.database import db
from datetime import datetime
import unittest
from App.models import Competition, Student
from App.tests.test_base import BaseTestCase

class IntegrationTestCase(BaseTestCase):
    def test_user_registration_and_login(self):
        user = Student(username="ryan", password="ryanpass")
        user.set_password("ryanpass")
        db.session.add(user)
        db.session.commit()

        retrieved_user = Student.query.filter_by(username="ryan").first()
        self.assertIsNotNone(retrieved_user)
        self.assertTrue(retrieved_user.check_password("ryanpass"))

    def test_competition_creation_and_student_participation(self):
        competition = Competition(
            name="RunTime",
            date=datetime.strptime("2024-06-09", "%Y-%m-%d").date(),
            location="St. Augustine",
            level=1,
            max_score=25,
            type="single"
        )
        db.session.add(competition)
        db.session.commit()

        student = Student(username="student1", password="studentpass")
        db.session.add(student)
        db.session.commit()

        competition.students.append(student)
        db.session.commit()

        competition_from_db = Competition.query.get(competition.id)
        self.assertEqual(len(competition_from_db.students), 1)
        self.assertEqual(competition_from_db.students[0].username, "student1")


if __name__ == '__main__':
    unittest.main()
