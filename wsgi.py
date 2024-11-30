
import csv, os, click
import pytest
from flask.cli import with_appcontext
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import *
import sys


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    db.create_all()


    with open("students.csv") as student_file:
        reader = csv.DictReader(student_file)

        for student in reader:
            stud = create_student(student['username'], student['password'])

    
    student_file.close()

    with open("moderators.csv") as moderator_file:
        reader = csv.DictReader(moderator_file)

        for moderator in reader:
            mod = create_moderator(moderator['username'], moderator['password'])

    moderator_file.close()

    with open("competitions.csv") as competition_file:
        reader = csv.DictReader(competition_file)

        for competition in reader:
            comp = create_competition(competition['mod_name'], competition['comp_name'], competition['date'], competition['location'], competition['level'], competition['max_score'], competition['type'])
    
    competition_file.close()
    
    with open("results.csv") as results_file:
        reader = csv.DictReader(results_file)

        if comp.type == "team":
            for result in reader:
                students = [result['student1'], result['student2'], result['student3']]
                team = add_team(result['mod_name'], result['comp_name'], result['team_name'], students)
                add_results(result['mod_name'], result['comp_name'], result['team_name'], int(result['score']))
    
    results_file.close()

    with open("competitions.csv") as competitions_file:
        reader = csv.DictReader(competitions_file)

        for competition in reader:
            if competition['comp_name'] != 'TopCoder':
                update_ratings(competition['mod_name'], competition['comp_name'])
                comp = create_competition(competition['mod_name'], competition['comp_name'], competition['date'], competition['location'], competition['level'], competition['max_score'], competition['type'])
                update_rankings(competition['comp_name'])
    
    competitions_file.close()





@app.cli.command("test")
@click.argument('test_name', type=str, required=True)
@with_appcontext
def run_tests(test_name):
    """Run a specific test file. Provide the test file name (e.g., 'competition')."""
    test_file = f"App/tests/test_{test_name}.py"
    
    # Print the full path for debugging
    full_path = os.path.abspath(test_file)
    print(f"Looking for test file at: {full_path}")
    
    # Check if the file exists
    if not os.path.exists(test_file):
        print(f"Error: Test file '{test_file}' not found!")
        sys.exit(1)

    # Run the test file with pytest
    result = pytest.main([test_file, "-v"])
    
    # Exit with the pytest result code
    sys.exit(result)


    

