from flask import Blueprint, render_template, redirect, url_for, request, session

user = Blueprint('user', __name__)

@user.route('/')
def home():
    return render_template('index.html')

@user.route('/login')
def login():
    return render_template('login.html')