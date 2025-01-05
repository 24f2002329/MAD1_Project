from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.models import db, User
from datetime import datetime

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        dob = request.form['dob']

        # Convert dob to datetime object
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date of birth format!', 'error')
            return redirect(url_for('auth.register'))

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'error')
            return redirect(url_for('auth.register'))

        # Create new user
        new_user = User(
            username=username,
            full_name=full_name.lower(),
            dob=dob,
            password=password
        )
        # new_user.set_password(password)  # Use the set_password method for hashing
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.user_login'))

    return render_template('register.html')


@auth_blueprint.route('/user-login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Authenticate user
        user = User.query.filter_by(username=username).first()
        # if user and check_password_hash(user.password, password):
        if user and user.password == password:      # Directly compare raw passwords
            # Store user details in session
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username    
            # flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard'))  # Adjust 'user.dashboard' to your actual route
        
        flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html')



@auth_blueprint.route('/forgot-username-password', methods=['GET', 'POST'])
def forgot_username_password():
    if request.method == 'POST':
        forgot_option = request.form.get('forgot_option')  # Get the selected option

        if forgot_option == 'forgot-password':
            # Handling Forgot Password Case
            username = request.form.get('username')
            dob = request.form.get('dob')
            
            # Find user by username and date of birth
            user = User.query.filter_by(username=username, dob=dob).first()
            if user:
                flash(f'Your password is {user.password}', 'info')  # For development only
                return redirect(url_for('auth.user_login'))
            flash('Invalid username or date of birth. Please try again.', 'error')

        elif forgot_option == 'forgot-username':
            # Handling Forgot Username Case
            name = request.form.get('full_name').lower()
            dob = request.form.get('dob')
            email = request.form.get('email')  # Optional field
            
            
            # Find user by name and dob (email is optional)
            user = User.query.filter_by(full_name=name, dob=dob).first()
            if user:
                flash(f'Your username is {user.username}', 'info')
                return redirect(url_for('auth.user_login'))
            flash('User not found. Please try again.', 'error')

    return render_template('forgot_username_password.html')







@auth_blueprint.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.user_login'))
