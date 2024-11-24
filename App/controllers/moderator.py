from App.database import db
from App.models import Moderator, Competition, Team, CompetitionTeam, Student, CompetitionStudent

def create_moderator(username, password):
    mod = get_moderator_by_username(username)
    if mod:
        print(f'{username} already exists!')
        return None

    newMod = Moderator(username=username, password=password)
    try:
        db.session.add(newMod)
        db.session.commit()
        print(f'New Moderator: {username} created!')
        return newMod
    except Exception as e:
        db.session.rollback()
        print(f'Something went wrong creating {username}')
        return None

def get_moderator_by_username(username):
    return Moderator.query.filter_by(username=username).first()

def get_moderator(id):
    return Moderator.query.get(id)

def get_all_moderators():
    return Moderator.query.all()

def get_all_moderators_json():
    mods = Moderator.query.all()
    if not mods:
        return []
    mods_json = [mod.get_json() for mod in mods]
    return mods_json

def update_moderator(id, username):
    mod = get_moderator(id)
    if mod:
        mod.username = username
        try:
            db.session.add(mod)
            db.session.commit()
            print("Username was updated!")
            return mod
        except Exception as e:
            db.session.rollback()
            print("Username was not updated!")
            return None
    print("ID: {id} does not exist!")
    return None

def add_mod(mod1_name, comp_name, mod2_name):
    mod1 = Moderator.query.filter_by(username=mod1_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()
    mod2 = Moderator.query.filter_by(username=mod2_name).first()

    if not mod1:
        print(f'Moderator: {mod1_name} not found!')
        return None
    elif not comp:
        print(f'Competition: {comp_name} not found!')
        return None
    elif not mod2:
        print(f'Moderator: {mod2_name} not found!')
        return None
    elif not mod1 in comp.moderators:
        print(f'{mod1_name} is not authorized to add results for {comp_name}!')
        return None
    else:
        return comp.add_mod(mod2)
                
def add_results(mod_name, comp_name, identifier, score):
    mod = Moderator.query.filter_by(username=mod_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()

    if not mod:
        print(f'{mod_name} was not found!')
        return None
    if not comp:
        print(f'{comp_name} was not found!')
        return None
    elif comp.confirm:
        print(f'Results for {comp_name} have already been finalized!')
        return None
    elif mod not in comp.moderators:
        print(f'{mod_name} is not authorized to add results for {comp_name}!')
        return None

    if comp.type == "team":
        teams = Team.query.filter_by(name=identifier).all()
        for team in teams:
            comp_team = CompetitionTeam.query.filter_by(comp_id=comp.id, team_id=team.id).first()
            if comp_team:
                comp_team.points_earned = score
                comp_team.rating_score = (score / comp.max_score) * 20 * comp.level
                try:
                    db.session.add(comp_team)
                    db.session.commit()
                    print(f'Score successfully added for {team.name}!')
                    return comp_team
                except Exception as e:
                    db.session.rollback()
                    print("Error saving team result")
                    return None

    elif comp.type == "single":
        student = Student.query.filter_by(username=identifier).first()
        if student:
            comp_student = CompetitionStudent.query.filter_by(comp_id=comp.id, student_id=student.id).first()
            if comp_student:
                comp_student.score = score  # Update existing student's score
            else:
                comp_student = CompetitionStudent(comp_id=comp.id, student_id=student.id, score=score)
                db.session.add(comp_student)
            try:
                db.session.commit()
                print(f'Score successfully added for {student.username}!')
                return comp_student
            except Exception as e:
                db.session.rollback()
                print("Error saving student result")
                return None

    return None




        
def update_ratings(mod_name, comp_name):
    mod = Moderator.query.filter_by(username=mod_name).first()
    comp = Competition.query.filter_by(name=comp_name).first()

    if not mod:
        print(f'{mod_name} was not found!')
        return None
    elif not comp:
        print(f'{comp_name} was not found!')
        return None
    elif comp.confirm:
        print(f'Results for {comp_name} have already been finalized!')
        return None
    elif mod not in comp.moderators:
        print(f'{mod_name} is not authorized to add results for {comp_name}!')
        return None
    elif comp.type == "team" and len(comp.teams) == 0:
        print(f'No teams found. Results cannot be confirmed!')
        return None

    if comp.type == "team":
        comp_teams = CompetitionTeam.query.filter_by(comp_id=comp.id).all()
        participating_team_ids = {comp_team.team_id for comp_team in comp_teams}
        #set deduction of points based on level for team competition
        if comp.level == 1:
            deduction_team = 0
        elif comp.level==2:
            deduction_team =1.3
        elif comp.level == 3:
            deduction_team=1.5
        else:
            deduction_team=0
        
        for comp_team in comp_teams:
            team = Team.query.filter_by(id=comp_team.team_id).first()
            for stud in team.students:
                stud.rating_score = (stud.rating_score * stud.comp_count + comp_team.rating_score) / (stud.comp_count + 1)
                stud.comp_count += 1
                db.session.add(stud)
        
        
        participating_team_ids = db.session.query(CompetitionTeam.team_id).filter_by(comp_id=comp.id).subquery()
        non_participating_team = Student.query.filter(Student.id.notin_(participating_team_ids)).all()
        
        #deduct points from students
        for stud in non_participating_team:
            stud.rating_score = stud.rating_score - deduction_team
            print(f"ID: {stud.id}, Name: {stud.username}, Rating Score: {stud.rating_score}, Competition Count: {stud.comp_count}")
     
        db.session.add(stud)
    
        try:
                db.session.commit()
        except Exception as e:
                db.session.rollback()   
                print(f"An error occurred while updating ratings: {e}")  
                
           

    elif comp.type == "single":
        competition_students = CompetitionStudent.query.filter_by(comp_id=comp.id).all()
        participating_student_ids = {comp_student.student_id for comp_student in competition_students}
        
        #set deduction of points based on level for single competition
        if comp.level == 1:
            deduction = 1.1
        elif comp.level ==2:
            deduction =1.5
        elif comp.level ==3:
            deduction = 1.8
        else:
            deduction= 0


        for comp_student in competition_students:
            student = Student.query.filter_by(id=comp_student.student_id).first()
            if not student:
                continue  # Skip if the student record is not found

            score = comp_student.score
            student.rating_score = (student.rating_score * student.comp_count + score) / (student.comp_count + 1)
            student.comp_count += 1
            db.session.add(student)
            print(f"ID: {student.id}, Name: {student.username}, Rating Score: {student.rating_score}, Competition Count: {student.comp_count}")
            
        participating_student_ids = db.session.query(CompetitionStudent.student_id).filter_by(comp_id=comp.id).subquery()
        non_participating_students = Student.query.filter(Student.id.notin_(participating_student_ids)).all()
        
        #deduct points from students
        for student in non_participating_students:
            student.rating_score = student.rating_score - deduction
            print(f"ID: {student.id}, Name: {student.username}, Rating Score: {student.rating_score}, Competition Count: {student.comp_count}")

        
        
            
        db.session.add(student)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred while updating ratings: {e}")

    # Mark the competition as confirmed
    comp.confirm = True
    try:
        db.session.add(comp)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred while confirming the competition: {e}")

    print(f"Results for {comp_name} finalized!")
    return True
