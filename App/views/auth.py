from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import login_required, login_user, current_user, logout_user
from App.models import db
from App.controllers import *


from.index import index_views

from App.controllers import *

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''


@auth_views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student = get_student_by_username(request.form['username'])
        moderator = get_moderator_by_username(request.form['username'])
        if student:
            if request.form['username'] == student.username and student.check_password(request.form['password']):
                login_user(student)
                session['user_type'] = 'student'
                return render_template('leaderboard.html', leaderboard=display_rankings(), user=current_user)
        if moderator:
            if request.form['username'] == moderator.username and moderator.check_password(request.form['password']):
                login_user(moderator)
                session['user_type'] = 'moderator'
                return render_template('leaderboard.html', leaderboard=display_rankings(), user=current_user)
    return render_template('login.html', user=current_user)



@auth_views.route('/logout')
@login_required
def logout():
    logout_user()
    session['user_type'] = None
    return render_template('leaderboard.html', leaderboard=display_rankings(), user=current_user)



@auth_views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        student = create_student(request.form['username'], request.form['password'])
        
        if student:
            if request.form['username'] == student.username:
                login_user(student)
                session['user_type'] = 'student'
                return render_template('leaderboard.html', leaderboard=display_rankings(), user=current_user)
    
    return render_template('signup.html', user=current_user)
