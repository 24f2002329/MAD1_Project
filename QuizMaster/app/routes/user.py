from flask import Blueprint, render_template, session, redirect, url_for, request, flash

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return render_template('index.html')
    
    return render_template('user_dashboard.html', username=session['username'])

@user_blueprint.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.user_login'))

    return render_template('profile.html', username=session['username'])

@user_blueprint.route('/scores' , methods=['GET', 'POST'])
def scores():
    if 'user_id' not in session:
        return redirect(url_for('auth.user_login'))

    if request.method == 'POST':
        # Save scores
        pass

    return render_template('scores.html')

@user_blueprint.route('/summary' , methods=['GET', 'POST'])
def summary():
    if 'user_id' not in session:
        return redirect(url_for('auth.user_login'))

    if request.method == 'POST':
        # Save summary
        pass

    return render_template('summary.html')

