import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash
from App.main import create_app
from App.database import db, create_db
from App.models import *
from App.controllers import *

LOGGER = logging.getLogger(__name__)

# Setup the Flask app and test database context
class UnitTests(unittest.TestCase):

    def setUp(self):
        # Create the app instance for testing
        self.app = create_app()
        self.app.config['TESTING'] = True  # Enable testing mode
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
        
        # Push an application context so that DB can be accessed
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()  # Create all tables in the in-memory DB

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()  # Clean up after each test
            db.drop_all()  # Drop all tables to reset the DB for the next test

    # User Unit Tests
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

    # Student Unit Tests
    def test_new_student(self):
        student = Student("dan", "jamespass")
        assert student.username == "dan"

    def test_student_get_json(self):
        student = Student("james", "jamespass")
        self.assertDictEqual(student.get_json(), {"id": None, "username": "james", "rating_score": 0, "comp_count": 0, "curr_rank": 0})

    # Moderator Unit Tests
    def test_new_moderator(self):
        mod = Moderator("robert", "robertpass")
        assert mod.username == "robert"

    def test_moderator_get_json(self):
        mod = Moderator("robert", "robertpass")
        self.assertDictEqual(mod.get_json(), {"id": None, "username": "robert", "competitions": []})

    # Team Unit Tests
    def test_new_team(self):
        team = Team("Scrum Lords")
        assert team.name == "Scrum Lords"

    def test_team_get_json(self):
        team = Team("Scrum Lords")
        self.assertDictEqual(team.get_json(), {"id": None, "name": "Scrum Lords", "students": []})

    # Competition Unit Tests
    def test_new_competition(self):
        competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25, "coding")
        assert competition.name == "RunTime" and competition.date.strftime("%d-%m-%Y") == "09-02-2024" and competition.location == "St. Augustine" and competition.level == 1 and competition.max_score == 25

    def test_competition_get_json(self):
        competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25, "coding")
        self.assertDictEqual(competition.get_json(), {"id": None, "name": "RunTime", "date": "09-02-2024", "location": "St. Augustine", "level": 1, "max_score": 25, "type": "coding", "moderators": [], "teams": [], "students": []})

    def test_add_moderator(self):
        competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25, "coding")
        mod = Moderator(username="robert", password="robertpass")
        
        db.session.add(competition)
        db.session.add(mod)
        db.session.commit()
        
        # Add moderator to competition
        comp_mod = competition.add_mod(mod)
        self.assertEqual(len(competition.moderators), 1)
        self.assertEqual(competition.moderators[0].username, "robert")

    def test_add_team(self):
        competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25, "coding")
        team = Team(name="Scrum Lords")
        
        db.session.add(competition)
        db.session.add(team)
        db.session.commit()
        
        # Add team to competition
        comp_team = competition.add_team(team)
        self.assertEqual(len(competition.teams), 1)
        self.assertEqual(competition.teams[0].name, "Scrum Lords")

    def test_add_student(self):
        competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25, "coding")
        student = Student(username="dan", password="danpass")
        
        db.session.add(competition)
        db.session.add(student)
        db.session.commit()
        
        # Add student to competition
        competition.add_student(student, score=20)
        
        # Verify the student is added to the competition with the correct score
        comp_student = CompetitionStudent.query.filter_by(comp_id=competition.id, student_id=student.id).first()
        self.assertEqual(comp_student.score, 20)

    def test_competition_with_data(self):
      # Create a competition with moderators, teams, and students
      competition = Competition("RunTime", datetime.strptime("09-02-2024", "%d-%m-%Y"), "St. Augustine", 1, 25, "coding")
      mod = Moderator(username="robert", password="robertpass")
      team = Team(name="Scrum Lords")
      student = Student(username="dan", password="danpass")

      db.session.add(competition)
      db.session.add(mod)
      db.session.add(team)
      db.session.add(student)
      db.session.commit()

      # Add moderator, team, and student to the competition
      competition.add_mod(mod)
      competition.add_team(team)
      
      # Add student and score to the competition
      competition.add_student(student, score=20)

      # Get the JSON representation of the competition
      result = competition.get_json()

      # Define the expected JSON structure with moderators, teams, and students
      expected = {
          "id": 1,
          "name": "RunTime",
          "date": "09-02-2024",
          "location": "St. Augustine",
          "level": 1,
          "max_score": 25,
          "type": "coding",
          "moderators": ["robert"],
          "teams": ["Scrum Lords"],
          "students": [
              {"username": "dan"}
          ]
      }

      # Check if the resulting JSON matches the expected structure
      self.assertDictEqual(result, expected)

    # Notification Unit Tests
    def test_new_notification(self):
        notification = Notification(1, "Ranking changed!")
        assert notification.student_id == 1 and notification.message == "Ranking changed!"

    def test_notification_get_json(self):
        notification = Notification(1, "Ranking changed!")
        self.assertDictEqual(notification.get_json(), {"id": None, "student_id": 1, "notification": "Ranking changed!"})

    # CompetitionTeam Unit Tests
    def test_new_competition_team(self):
        competition_team = CompetitionTeam(1, 1)
        assert competition_team.comp_id == 1 and competition_team.team_id == 1

    def test_competition_team_update_points(self):
        competition_team = CompetitionTeam(1, 1)
        competition_team.update_points(15)
        assert competition_team.points_earned == 15

    def test_competition_team_update_rating(self):
        competition_team = CompetitionTeam(1, 1)
        competition_team.update_rating(12)
        assert competition_team.rating_score == 12

    def test_competition_team_get_json(self):
        competition_team = CompetitionTeam(1, 1)
        competition_team.update_points(15)
        competition_team.update_rating(12)
        self.assertDictEqual(competition_team.get_json(), {"id": None, "team_id": 1, "competition_id": 1, "points_earned": 15, "rating_score": 12})

    # CompetitionModerator Unit Tests
    def test_new_competition_moderator(self):
        competition_moderator = CompetitionModerator(1, 1)
        assert competition_moderator.comp_id == 1 and competition_moderator.mod_id == 1

    def test_competition_moderator_get_json(self):
        competition_moderator = CompetitionModerator(1, 1)
        self.assertDictEqual(competition_moderator.get_json(), {"id": None, "competition_id": 1, "moderator_id": 1})

    # StudentTeam Unit Tests
    def test_new_student_team(self):
        student_team = StudentTeam(1, 1)
        assert student_team.student_id == 1 and student_team.team_id == 1

    def test_student_team_get_json(self):
        student_team = StudentTeam(1, 1)
        self.assertDictEqual(student_team.get_json(), {"id": None, "student_id": 1, "team_id": 1})

        # RankingHistory Unit Tests
    def test_new_ranking_history(self):
        # Create a student object
        student = Student(username="dan", password="danpass")
        db.session.add(student)
        db.session.commit()

        # Create a RankingHistory entry
        rank_history = RankingHistory(student_id=student.id, date=datetime(2024, 11, 27), rank=1, rating=1500)
        db.session.add(rank_history)
        db.session.commit()

        # Test if the ranking history entry is created correctly
        self.assertEqual(rank_history.student_id, student.id)
        self.assertEqual(rank_history.rank, 1)
        self.assertEqual(rank_history.rating, 1500)
        self.assertEqual(rank_history.date, datetime(2024, 11, 27))

    def test_ranking_history_to_dict(self):
        # Create a student object
        student = Student(username="dan", password="danpass")
        db.session.add(student)
        db.session.commit()

        # Create a RankingHistory entry
        rank_history = RankingHistory(student_id=student.id, date=datetime(2024, 11, 27), rank=1, rating=1500)
        
        # Get the dictionary representation of the object
        result_dict = rank_history.to_dict()

        # Expected dictionary format
        expected_dict = {
            "id": None,  # The ID will be None until the object is committed
            "student_id": student.id,
            "date": datetime(2024, 11, 27),
            "rank": 1,
            "rating": 1500
        }

        # Compare the returned dictionary with the expected one
        self.assertDictEqual(result_dict, expected_dict)

    def test_ranking_history_in_db(self):
        # Create a student object
        student = Student(username="dan", password="danpass")
        db.session.add(student)
        db.session.commit()

        # Create a RankingHistory entry
        rank_history = RankingHistory(student_id=student.id, date=datetime(2024, 11, 27), rank=1, rating=1500)
        db.session.add(rank_history)
        db.session.commit()

        # Query the database to verify that the ranking history was saved
        saved_rank_history = RankingHistory.query.first()
        self.assertEqual(saved_rank_history.student_id, student.id)
        self.assertEqual(saved_rank_history.rank, 1)
        self.assertEqual(saved_rank_history.rating, 1500)
        self.assertEqual(saved_rank_history.date, datetime(2024, 11, 27))




class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Integration Test: User Registration and Login
    def test_user_registration_and_login(self):
        user = Student(username="ryan", password="ryanpass")
        user.set_password("ryanpass")
        db.session.add(user)
        db.session.commit()

        retrieved_user = Student.query.filter_by(username="ryan").first()
        self.assertIsNotNone(retrieved_user)
        self.assertTrue(retrieved_user.check_password("ryanpass"))

    # Integration Test: Competition Creation and Student Participation
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
        #student.set_password()
        db.session.add(student)
        db.session.commit()

        competition.students.append(student)
        db.session.commit()

        competition_from_db = Competition.query.get(competition.id)
        self.assertEqual(competition_from_db.name, "RunTime")
        self.assertEqual(len(competition_from_db.students), 1)
        self.assertEqual(competition_from_db.students[0].username, "student1")

    # Integration Test: Create a Team and Add Members
    def test_create_team_and_add_members(self):
        team = Team(name="Scrum Lords")
        db.session.add(team)
        db.session.commit()

        student = Student(username="student2", password="studentpass2")
         #student.set_password("studentpass2")
        db.session.add(student)
        db.session.commit()

        team.students.append(student)
        db.session.commit()

        team_from_db = Team.query.get(team.id)
        self.assertEqual(team_from_db.name, "Scrum Lords")
        self.assertEqual(len(team_from_db.students), 1)
        self.assertEqual(team_from_db.students[0].username, "student2")

    # Integration Test: Competition Moderation
    def test_competition_moderation(self):
        competition = Competition(
            name="CodeChamp",
            date=datetime.strptime("2024-07-09", "%Y-%m-%d").date(),
            location="Port of Spain",
            level=2,
            max_score=50,
            type="single"
        )
        db.session.add(competition)
        db.session.commit()

        moderator = Moderator(username="mod1", password="modpass")
         #moderator.set_password("modpass")
        db.session.add(moderator)
        db.session.commit()

        competition.moderators.append(moderator)
        db.session.commit()

        competition_from_db = Competition.query.get(competition.id)
        self.assertEqual(len(competition_from_db.moderators), 1)
        self.assertEqual(competition_from_db.moderators[0].username, "mod1")

    # Integration Test: Notifications for Students
    def test_notifications_for_students(self):
        student = Student(username="dan", password="danpass")
        #student.set_password()
        db.session.add(student)
        db.session.commit()

        notification = Notification(student_id=student.id, message="Your rank has changed!")
        db.session.add(notification)
        db.session.commit()

        notifications = Notification.query.filter_by(student_id=student.id).all()
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].message, "Your rank has changed!")

    # Integration Test: Full Workflow (Competition and Teams)
    def test_full_competition_workflow(self):
        competition = Competition(
            name="FullTestComp",
            date=datetime.strptime("2024-09-09", "%Y-%m-%d").date(),
            location="Arima",
            level=3,
            max_score=100,
            type="team"
        )
        db.session.add(competition)
        db.session.commit()

        team = Team(name="Winners")
        db.session.add(team)
        db.session.commit()

        student = Student(username="stud3", password="studpass3")
        student.set_password("studpass3")
        db.session.add(student)
        db.session.commit()

        team.students.append(student)
        db.session.commit()
        competition.teams.append(team)
        competition.students.append(student)
        db.session.commit()

        competition_from_db = Competition.query.get(competition.id)
        self.assertEqual(len(competition_from_db.teams), 1)
        self.assertEqual(len(competition_from_db.students), 1)
        self.assertEqual(competition_from_db.teams[0].name, "Winners")
        self.assertEqual(competition_from_db.students[0].username, "stud3")


if __name__ == '__main__':
    unittest.main()




'''
    Integration Tests

class IntegrationTests(unittest.TestCase):
    
    #Feature 1 Integration Tests
    def test1_create_competition(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      assert comp.name == "RunTime" and comp.date.strftime("%d-%m-%Y") == "29-03-2024" and comp.location == "St. Augustine" and comp.level == 2 and comp.max_score == 25

    def test2_create_competition(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      self.assertDictEqual(comp.get_json(), {"id": 1, "name": "RunTime", "date": "29-03-2024", "location": "St. Augustine", "level": 2, "max_score": 25, "moderators": ["debra"], "teams": []})
      
    #Feature 2 Integration Tests
    def test1_add_results(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      students = [student1.username, student2.username, student3.username]
      team = add_team(mod.username, comp.name, "Runtime Terrors", students)
      comp_team = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      assert comp_team.points_earned == 15
    
    def test2_add_results(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      students = [student1.username, student2.username, student3.username]
      add_team(mod.username, comp.name, "Runtime Terrors", students)
      comp_team = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students = [student1.username, student4.username, student5.username]
      team = add_team(mod.username, comp.name, "Scrum Lords", students)
      assert team == None
    
    def test3_add_results(self):
      db.drop_all()
      db.create_all()
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      comp = create_competition(mod1.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      students = [student1.username, student2.username, student3.username]
      team = add_team(mod2.username, comp.name, "Runtime Terrors", students)
      assert team == None

    #Feature 3 Integration Tests
    def test_display_student_info(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      students = [student1.username, student2.username, student3.username]
      team = add_team(mod.username, comp.name, "Runtime Terrors", students)
      comp_team = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      update_ratings(mod.username, comp.name)
      update_rankings()
      self.assertDictEqual(display_student_info("james"), {"profile": {'id': 1, 'username': 'james', 'rating_score': 24.0, 'comp_count': 1, 'curr_rank': 1}, "competitions": ['RunTime']})

    #Feature 4 Integration Tests
    def test_display_competition(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      student7 = create_student("isabella", "isabellapass")
      student8 = create_student("richard", "richardpass")
      student9 = create_student("jessica", "jessicapass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp.name, "Runtime Terrors", students1)
      comp_team1 = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp.name, "Scrum Lords", students2)
      comp_team2 = add_results(mod.username, comp.name, "Scrum Lords", 12)
      students3 = [student7.username, student8.username, student9.username]
      team3 = add_team(mod.username, comp.name, "Beyond Infinity", students3)
      comp_team = add_results(mod.username, comp.name, "Beyond Infinity", 10)
      update_ratings(mod.username, comp.name)
      update_rankings()
      self.assertDictEqual(comp.get_json(), {'id': 1, 'name': 'RunTime', 'date': '29-03-2024', 'location': 'St. Augustine', 'level': 2, 'max_score': 25, 'moderators': ['debra'], 'teams': ['Runtime Terrors', 'Scrum Lords', 'Beyond Infinity']})

    #Feature 5 Integration Tests
    def test_display_rankings(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp.name, "Runtime Terrors", students1)
      comp_team1 = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp.name, "Scrum Lords", students2)
      comp_team2 = add_results(mod.username, comp.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp.name)
      update_rankings()
      self.assertListEqual(display_rankings(), [{"placement": 1, "student": "james", "rating score": 24.0}, {"placement": 1, "student": "steven", "rating score": 24.0}, {"placement": 1, "student": "emily", "rating score": 24.0}, {"placement": 4, "student": "mark", "rating score": 16.0}, {"placement": 4, "student": "eric", "rating score": 16.0}, {"placement": 4, "student": "ryan", "rating score": 16.0}])

    #Feature 6 Integration Tests
    def test1_display_notification(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp.name, "Runtime Terrors", students1)
      comp_team1 = add_results(mod.username, comp.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp.name, "Scrum Lords", students2)
      comp_team2 = add_results(mod.username, comp.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp.name)
      update_rankings()
      self.assertDictEqual(display_notifications("james"), {"notifications": [{"ID": 1, "Notification": "RANK : 1. Congratulations on your first rank!"}]})

    def test2_display_notification(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024", "Macoya", 1, 30)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      comp1_team1 = add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp1.name, "Scrum Lords", students2)
      comp1_team2 = add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      update_rankings()
      students3 = [student1.username, student4.username, student5.username]
      team3 = add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      comp_team3 = add_results(mod.username, comp2.name, "Runtime Terrors", 15)
      students4 = [student2.username, student3.username, student6.username]
      team4 = add_team(mod.username, comp2.name, "Scrum Lords", students4)
      comp_team4 = add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      update_rankings()
      self.assertDictEqual(display_notifications("james"), {"notifications": [{"ID": 1, "Notification": "RANK : 1. Congratulations on your first rank!"}, {"ID": 7, "Notification": "RANK : 1. Well done! You retained your rank."}]})

    def test3_display_notification(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024", "Macoya", 1, 20)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      comp1_team1 = add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp1.name, "Scrum Lords", students2)
      comp1_team2 = add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      update_rankings()
      students3 = [student1.username, student4.username, student5.username]
      team3 = add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      comp_team3 = add_results(mod.username, comp2.name, "Runtime Terrors", 20)
      students4 = [student2.username, student3.username, student6.username]
      team4 = add_team(mod.username, comp2.name, "Scrum Lords", students4)
      comp_team4 = add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      update_rankings()
      self.assertDictEqual(display_notifications("steven"), {"notifications": [{"ID": 2, "Notification": "RANK : 1. Congratulations on your first rank!"}, {"ID": 10, "Notification": "RANK : 4. Oh no! Your rank has went down."}]})

    def test4_display_notification(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024", "Macoya", 1, 20)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      comp1_team1 = add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp1.name, "Scrum Lords", students2)
      comp1_team2 = add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      update_rankings()
      students3 = [student1.username, student4.username, student5.username]
      team3 = add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      comp_team3 = add_results(mod.username, comp2.name, "Runtime Terrors", 20)
      students4 = [student2.username, student3.username, student6.username]
      team4 = add_team(mod.username, comp2.name, "Scrum Lords", students4)
      comp_team4 = add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      update_rankings()
      self.assertDictEqual(display_notifications("mark"), {"notifications": [{"ID": 4, "Notification": "RANK : 4. Congratulations on your first rank!"}, {"ID": 8, "Notification": "RANK : 2. Congratulations! Your rank has went up."}]})

    #Additional Integration Tests
    def test1_add_mod(self):
      db.drop_all()
      db.create_all()
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      comp = create_competition(mod1.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      assert add_mod(mod1.username, comp.name, mod2.username) != None
       
    def test2_add_mod(self):
      db.drop_all()
      db.create_all()
      mod1 = create_moderator("debra", "debrapass")
      mod2 = create_moderator("robert", "robertpass")
      mod3 = create_moderator("raymond", "raymondpass")
      comp = create_competition(mod1.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      assert add_mod(mod2.username, comp.name, mod3.username) == None
    
    def test_student_list(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024", "Macoya", 1, 20)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      comp1_team1 = add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp1.name, "Scrum Lords", students2)
      comp1_team2 = add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      update_rankings()
      students3 = [student1.username, student4.username, student5.username]
      team3 = add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      comp_team3 = add_results(mod.username, comp2.name, "Runtime Terrors", 20)
      students4 = [student2.username, student3.username, student6.username]
      team4 = add_team(mod.username, comp2.name, "Scrum Lords", students4)
      comp_team4 = add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      update_rankings()
      self.assertEqual(get_all_students_json(), [{'id': 1, 'username': 'james', 'rating_score': 22, 'comp_count': 2, 'curr_rank': 1}, {'id': 2, 'username': 'steven', 'rating_score': 17, 'comp_count': 2, 'curr_rank': 4}, {'id': 3, 'username': 'emily', 'rating_score': 17, 'comp_count': 2, 'curr_rank': 4}, {'id': 4, 'username': 'mark', 'rating_score': 18, 'comp_count': 2, 'curr_rank': 2}, {'id': 5, 'username': 'eric', 'rating_score': 18, 'comp_count': 2, 'curr_rank': 2}, {'id': 6, 'username': 'ryan', 'rating_score': 13, 'comp_count': 2, 'curr_rank': 6}])

    def test_comp_list(self):
      db.drop_all()
      db.create_all()
      mod = create_moderator("debra", "debrapass")
      comp1 = create_competition(mod.username, "RunTime", "29-03-2024", "St. Augustine", 2, 25)
      comp2 = create_competition(mod.username, "Hacker Cup", "23-02-2024", "Macoya", 1, 20)
      student1 = create_student("james", "jamespass")
      student2 = create_student("steven", "stevenpass")
      student3 = create_student("emily", "emilypass")
      student4 = create_student("mark", "markpass")
      student5 = create_student("eric", "ericpass")
      student6 = create_student("ryan", "ryanpass")
      students1 = [student1.username, student2.username, student3.username]
      team1 = add_team(mod.username, comp1.name, "Runtime Terrors", students1)
      comp1_team1 = add_results(mod.username, comp1.name, "Runtime Terrors", 15)
      students2 = [student4.username, student5.username, student6.username]
      team2 = add_team(mod.username, comp1.name, "Scrum Lords", students2)
      comp1_team2 = add_results(mod.username, comp1.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp1.name)
      update_rankings()
      students3 = [student1.username, student4.username, student5.username]
      team3 = add_team(mod.username, comp2.name, "Runtime Terrors", students3)
      comp_team3 = add_results(mod.username, comp2.name, "Runtime Terrors", 20)
      students4 = [student2.username, student3.username, student6.username]
      team4 = add_team(mod.username, comp2.name, "Scrum Lords", students4)
      comp_team4 = add_results(mod.username, comp2.name, "Scrum Lords", 10)
      update_ratings(mod.username, comp2.name)
      update_rankings()
      self.assertListEqual(get_all_competitions_json(), [{"id": 1, "name": "RunTime", "date": "29-03-2024", "location": "St. Augustine", "level": 2, "max_score": 25, "moderators": ["debra"], "teams": ["Runtime Terrors", "Scrum Lords"]}, {"id": 2, "name": "Hacker Cup", "date": "23-02-2024", "location": "Macoya", "level": 1, "max_score": 20, "moderators": ["debra"], "teams": ["Runtime Terrors", "Scrum Lords"]}])
      '''