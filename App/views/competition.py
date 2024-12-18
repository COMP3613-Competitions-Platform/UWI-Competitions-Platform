from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import current_user, login_required
from.index import index_views
from App.controllers import *

comp_views = Blueprint('comp_views', __name__, template_folder='../templates')


@comp_views.route('/competitions', methods=['GET'])
def get_competitions():
    competitions = get_all_competitions_json()
    return render_template('competitions.html', competitions=get_all_competitions(), user=current_user)
 

#create new comp
@comp_views.route('/createcompetition', methods=['POST'])
@login_required
def create_comp():
    data = request.form
    
    if session['user_type'] == 'moderator':
        moderator = Moderator.query.filter_by(id=current_user.id).first()
    else:
        moderator = None

    date = data['date']
    date = date[8] + date[9] + '-' + date[5] + date[6] + '-' + date[0] + date[1] + date[2] + date[3]
    
    response = create_competition(moderator.username, data['name'], date, data['location'], data['level'], data['max_score'], data['type'])
    return render_template('competitions.html', competitions=get_all_competitions(), user=current_user)


#page to create new comp
@comp_views.route('/createcompetition', methods=['GET'])
def create_comp_page():
    return render_template('competition_creation.html', user=current_user)


@comp_views.route('/competitions/<int:id>', methods=['GET'])
def competition_details(id):
    competition = get_competition(id)
    if not competition:
        return render_template('404.html')
    
    #team = get_all_teams()

    #teams = get_participants(competition_name)
    if current_user.is_authenticated:
        if session['user_type'] == 'moderator':
            moderator = Moderator.query.filter_by(id=current_user.id).first()
        else:
            moderator = None
    else:
        moderator = None
    
    leaderboard = display_competition_results(competition.name)
    return render_template('competition_details.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)#, team=team)


@comp_views.route('/competition/<string:name>', methods=['GET'])
def competition_details_by_name(name):
    competition = get_competition_by_name(name)
    if not competition:
        return render_template('404.html')

    #teams = get_participants(competition_name)
    if current_user.is_authenticated:
        if session['user_type'] == 'moderator':
            moderator = Moderator.query.filter_by(id=current_user.id).first()
        else:
            moderator = None
    else:
        moderator = None
    
    leaderboard = display_competition_results(name)

    return render_template('competition_details.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)
    

@comp_views.route('/add_results/<int:comp_id>', methods=['GET'])
def add_results_page(comp_id):
    competition = get_competition(comp_id)
    if session['user_type'] == 'moderator':
        moderator = Moderator.query.filter_by(id=current_user.id).first()
    else:
        moderator = None

    leaderboard = display_competition_results(competition.name)

    return render_template('competition_results.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)




@comp_views.route('/add_results/<string:comp_name>', methods=['POST'])
def add_competition_results(comp_name):
    competition = get_competition_by_name(comp_name)
    
    if session['user_type'] == 'moderator':
        moderator = Moderator.query.filter_by(id=current_user.id).first()
    else:
        moderator = None
    
    data = request.form
    
    if competition.type == "team":
        students = [data['student1'], data['student2'], data['student3']]
        response = add_team(moderator.username, comp_name, data['team_name'], students)
    
    elif competition.type == "single":
        student = Student.query.filter_by(username=data['student_name']).first()
        score = int(data['score']) 
        if student:
            response = competition.add_student(student, score)
        else:
            print(f"Student {data['student_name']} not found!")

    if competition.type == "team" and response:
        response = add_results(moderator.username, comp_name, data['team_name'], int(data['score']))
    elif competition.type == "single" and response:
        response = add_results(moderator.username, comp_name, data['student_name'], int(data['score']))

    leaderboard = display_competition_results(comp_name)

    return render_template('competition_details.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)

    



@comp_views.route('/confirm_results/<string:comp_name>', methods=['GET', 'POST'])
def confirm_results(comp_name):
    if session['user_type'] == 'moderator':
        moderator = Moderator.query.filter_by(id=current_user.id).first()
    else:
        moderator = None
    
    competition = get_competition_by_name(comp_name)

    if update_ratings(moderator.username, competition.name):
        update_rankings(competition.name)

    leaderboard = display_competition_results(comp_name)

    return render_template('competition_details.html', competition=competition, moderator=moderator, leaderboard=leaderboard, user=current_user)


@comp_views.route('/competitions_postman', methods=['GET'])
def get_competitions_postman():
    competitions = get_all_competitions_json()
    return (jsonify(competitions),200)


@comp_views.route('/createcompetition_postman', methods=['POST'])
def create_comp_postman():
    data = request.json
    
    response = create_competition(
        mod_name='robert',  
        comp_name=data['name'],  
        date=data['date'],  
        location=data['location'],  
        level=data['level'],  
        max_score=data['max_score'],  
        type=data['type']  
    )

   
    if response:
        return jsonify({'message': "Competition created!"}), 201
    return jsonify({'error': "Error creating competition"}), 500


@comp_views.route('/competitions_postman/<int:id>', methods=['GET'])
def competition_details_postman(id):
    competition = get_competition(id)
    if not competition:
        return (jsonify({'error': "Competition not found"}),404)
    
    
    if current_user.is_authenticated:
        if session['user_type'] == 'moderator':
            moderator = Moderator.query.filter_by(id=current_user.id).first()
        else:
            moderator = None
    else:
        moderator = None
    
    leaderboard = display_competition_results(competition.name)
    return (jsonify(competition.toDict()),200)

@comp_views.route('/add_results_postman/<string:comp_name>', methods=['POST'])
def add_competition_results_postman(comp_name):
    # Fetch competition by name
    competition = get_competition_by_name(comp_name)
    if not competition:
        return jsonify({'error': f"Competition '{comp_name}' not found!"}), 404

    data = request.json

    # Handle team competition
    if competition.type == "team":
        required_fields = ['student1', 'student2', 'student3', 'team_name', 'score']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f"Missing one or more fields: {required_fields}"}), 400

        # Add team results
        team_name = data['team_name']
        students = [data['student1'], data['student2'], data['student3']]
        add_team('robert', comp_name, team_name, students)
        response = add_results('robert', comp_name, team_name, int(data['score']))

    # Handle single competition
    elif competition.type == "single":
        required_fields = ['student_name', 'score']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f"Missing one or more fields: {required_fields}"}), 400

        # Add single competition results
        response = add_results('robert', comp_name, data['student_name'], int(data['score']))

    # Unsupported competition type
    else:
        return jsonify({'error': "Unsupported competition type!"}), 400

    # Return appropriate response
    if response:
        return jsonify({'message': "Results added successfully!"}), 201
    return jsonify({'error': "Error adding results!"}), 500
