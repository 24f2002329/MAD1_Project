from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.models import db, User

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')


@admin_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hardcoded admin credentials
        hardcoded_username = 'admin'
        hardcoded_password = 'devendra'  # In a real application, use a hashed password
        
        if username == hardcoded_username and password == hardcoded_password:
            session['user_id'] = 1  # Assuming the admin user ID is 1
            session['role'] = 'admin'
            session['username'] = hardcoded_username
            flash('Login successful, Hello Devendra!', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials. Please try again.', 'error')

    return render_template('admin_login.html')

@admin_blueprint.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return "Unauthorized", 403
    return render_template('admin_dashboard.html')