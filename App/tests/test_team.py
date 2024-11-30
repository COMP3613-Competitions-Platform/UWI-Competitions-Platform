import unittest
from App.models import Team
from App.tests.test_base import BaseTestCase



class TeamTestCase(BaseTestCase):
    def test_new_team(self):
        team = Team("Scrum Lords")
        assert team.name == "Scrum Lords"

    def test_team_get_json(self):
        team = Team("Scrum Lords")
        self.assertDictEqual(team.get_json(), {
            "id": None,
            "name": "Scrum Lords",
            "students": []
        })

if __name__ == '__main__':
    unittest.main()
