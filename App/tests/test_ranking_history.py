from App.database import db
from datetime import datetime
import unittest
from App.models import RankingHistory, Student
from App.tests.test_base import BaseTestCase



class RankingHistoryUnitTests(BaseTestCase):
    def test_new_ranking_history(self):
        student = Student(username="dan", password="danpass")
        db.session.add(student)
        db.session.commit()

        rank_history = RankingHistory(student_id=student.id, date=datetime(2024, 11, 27), rank=1, rating=1500)
        db.session.add(rank_history)
        db.session.commit()

        self.assertEqual(rank_history.student_id, student.id)
        self.assertEqual(rank_history.rank, 1)
        self.assertEqual(rank_history.rating, 1500)
        self.assertEqual(rank_history.date, datetime(2024, 11, 27))

    def test_ranking_history_to_dict(self):
        student = Student(username="dan", password="danpass")
        db.session.add(student)
        db.session.commit()

        rank_history = RankingHistory(student_id=student.id, date=datetime(2024, 11, 27), rank=1, rating=1500)
        
        result_dict = rank_history.to_dict()

        expected_dict = {
            "id": None,  
            "student_id": student.id,
            "date": datetime(2024, 11, 27),
            "rank": 1,
            "rating": 1500
        }
        self.assertDictEqual(result_dict, expected_dict)

    def test_ranking_history_in_db(self):
        student = Student(username="dan", password="danpass")
        db.session.add(student)
        db.session.commit()

        rank_history = RankingHistory(student_id=student.id, date=datetime(2024, 11, 27), rank=1, rating=1500)
        db.session.add(rank_history)
        db.session.commit()

        saved_rank_history = RankingHistory.query.first()
        self.assertEqual(saved_rank_history.student_id, student.id)
        self.assertEqual(saved_rank_history.rank, 1)
        self.assertEqual(saved_rank_history.rating, 1500)
        self.assertEqual(saved_rank_history.date, datetime(2024, 11, 27))

if __name__ == '__main__':
    unittest.main()