from App.database import db
from App.models import Competition, Moderator, CompetitionTeam, Team, Student, CompetitionStudent
from datetime import datetime

def create_competition(mod_name, comp_name, date, location, level, max_score, type):
    comp = get_competition_by_name(comp_name)
    if comp:
        print(f'{comp_name} already exists!')
        return None
    
    mod = Moderator.query.filter_by(username=mod_name).first()
    if mod:
        newComp = Competition(name=comp_name, date=datetime.strptime(date, "%d-%m-%Y"), location=location, level=level, max_score=max_score, type=type)
        try:
            newComp.add_mod(mod)
            db.session.add(newComp)
            db.session.commit()
            print(f'New Competition: {comp_name} created!')
            return newComp
        except Exception as e:
            db.session.rollback()
            print("Something went wrong!")
            return None
    else:
        print("Invalid credentials!")

def get_competition_by_name(name):
    return Competition.query.filter_by(name=name).first()

def get_competition(id):
    return Competition.query.get(id)

def get_all_competitions():
    return Competition.query.all()

def get_all_competitions_json():
    competitions = Competition.query.all()

    if not competitions:
        return []
    else:
        return [comp.get_json() for comp in competitions]

def display_competition_results(name):
    comp = get_competition_by_name(name)

    if not comp:
        print(f'{name} was not found!')
        return None
    
    leaderboard = []

    # For Team Competitions
    if comp.type == "team":
        if len(comp.teams) == 0:
            print(f'No teams found for {name}!')
            return []

        comp_teams = CompetitionTeam.query.filter_by(comp_id=comp.id).all()
        comp_teams.sort(key=lambda x: x.points_earned, reverse=True)

        count = 1
        curr_high = comp_teams[0].points_earned
        curr_rank = 1
        
        for comp_team in comp_teams:
            if curr_high != comp_team.points_earned:
                curr_rank = count
                curr_high = comp_team.points_earned

            team = Team.query.filter_by(id=comp_team.team_id).first()
            leaderboard.append({
                "placement": curr_rank, 
                "team": team.name, 
                "members": [student.username for student in team.students], 
                "score": comp_team.points_earned
            })
            count += 1

    # For Single Competitions
    elif comp.type == "single":
        if len(comp.students) == 0:
            print(f'No students found for {name}!')
            return []

        comp_students = CompetitionStudent.query.filter_by(comp_id=comp.id).all()
        comp_students.sort(key=lambda x: x.score, reverse=True)

        count = 1
        curr_high = comp_students[0].score
        curr_rank = 1

        for comp_student in comp_students:
            if curr_high != comp_student.score:
                curr_rank = count
                curr_high = comp_student.score

            student = Student.query.filter_by(id=comp_student.student_id).first()
            leaderboard.append({
                "placement": curr_rank, 
                "student": student.username, 
                "score": comp_student.score
            })
            count += 1

    return leaderboard


        
