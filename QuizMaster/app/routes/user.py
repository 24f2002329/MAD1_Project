from flask import Blueprint, render_template, redirect, url_for, request, session

user = Blueprint('user', __name__)

@user.route('/')
def home():
    return render_template('index.html')

@user.route('/login')
def login():
    return render_template('login.html')

@user.route('/scores')
def scores():
    return render_template('scores.html')

@user.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.home'))

@user.route('/summary')
def summary():
    return render_template('summary.html')

@user.route('/registration')
def registration():
    return render_template('registration.html')

@user.route('/forgot_username_password')
def forgot_username_password():
    return render_template('forgot_username_password.html')

@user.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@user.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')