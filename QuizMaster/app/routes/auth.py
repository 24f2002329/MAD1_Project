from flask import Blueprint, render_template, redirect, url_for, request, session
auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
    return render_template('index.html')

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/scores')
def scores():
    return render_template('scores.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.home'))

@auth.route('/summary')
def summary():
    return render_template('summary.html')