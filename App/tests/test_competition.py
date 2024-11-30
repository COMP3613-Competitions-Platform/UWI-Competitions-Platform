from datetime import datetime
import unittest
from App.models import Competition
from App.tests.test_base import BaseTestCase




class CompetitionTestCase(BaseTestCase):
    def test_new_competition(self):
        competition = Competition(
            "RunTime",
            datetime.strptime("09-02-2024", "%d-%m-%Y"),
            "St. Augustine",
            1,
            25,
            "single"
        )
        assert competition.name == "RunTime"

    def test_competition_get_json(self):
        competition = Competition(
            "RunTime",
            datetime.strptime("09-02-2024", "%d-%m-%Y"),
            "St. Augustine",
            1,
            25,
            "team"
        )
        self.assertDictEqual(competition.get_json(), {
            "id": None,
            "name": "RunTime",
            "date": "09-02-2024",
            "location": "St. Augustine",
            "level": 1,
            "max_score": 25,
            "type": "team",
            "moderators": [],
            "teams": [],
            "students": []
        })


if __name__ == '__main__':
    unittest.main()
