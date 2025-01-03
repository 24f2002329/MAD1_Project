from flask import Blueprint, render_template, redirect, url_for, request, session
auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
    return render_template('index.html')

@auth.route('/login')
def login():
    return render_template('login.html')