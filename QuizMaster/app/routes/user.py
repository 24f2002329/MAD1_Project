from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.models.models import *
from datetime import datetime

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


@user_blueprint.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))
    return render_template('index.html')



@user_blueprint.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session['user_id'] == 0:
        return render_template('index.html')
    upcoming_quizzes = Quiz.query.filter(Quiz.quiz_date >= datetime.today()).order_by(Quiz.quiz_date).all()
    return render_template('user/user_dashboard.html', username=session['username'], quizzes=upcoming_quizzes)


@user_blueprint.route('/scores' , methods=['GET', 'POST'])
def scores():
    if 'user_id' not in session:
        return redirect(url_for('auth.user_login'))

    if request.method == 'POST':
        # Save scores
        pass

    return render_template('user/scores.html')

@user_blueprint.route('/summary' , methods=['GET', 'POST'])
def summary():
    if 'user_id' not in session:
        return redirect(url_for('auth.user_login'))

    if request.method == 'POST':
        # Save summary
        pass

    return render_template('user/summary.html')


@user_blueprint.route('/profile', methods=['GET'])
def profile():
    user_id = session.get('user_id')
    if user_id is None or user_id == 0:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.user_login'))
    user = User.query.get(user_id)
    return render_template('user/profile.html', user=user)




@user_blueprint.route('/settings', methods=['GET', 'POST'])
def settings():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to access settings.', 'error')
        return redirect(url_for('auth.user_login'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.username = request.form.get('username')
        # Convert the date string to a Python date object
        dob_str = request.form.get('dob')
        if dob_str:
            try:
                user.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
                return redirect(url_for('user.settings'))
        user.password = request.form.get('password')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/settings.html', user=user)



@user_blueprint.route('/view_quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    return render_template('user/view_quiz.html', quiz=quiz)

from flask import jsonify

@user_blueprint.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash('You must be logged in to attempt the quiz.', 'error')
            return redirect(url_for('auth.user_login'))

        # Retrieve user's answers from the form
        answers = request.form.to_dict(flat=False)

        # Save the quiz attempt
        for question_id, answer_list in answers.items():
            if question_id.startswith('q'):
                question_id = int(question_id[1:])
                for answer in answer_list:
                    attempt = QuizAttempt(
                        user_id=user_id,
                        quiz_id=quiz_id,
                        question_id=question_id,
                        answer=answer,
                        attempt_date=datetime.now()
                    )
                    db.session.add(attempt)

        db.session.commit()
        flash('Quiz attempt saved successfully!', 'success')
        return redirect(url_for('user.dashboard'))

    current_question_index = 0  # Initialize the current question index

    # Serialize questions to JSON-compatible format
    serialized_questions = [
        {
            'id': question.id,
            'title': question.title,
            'type': question.type,
            'options': [
                {'id': 'option1', 'text': question.option1},
                {'id': 'option2', 'text': question.option2},
                {'id': 'option3', 'text': question.option3},
                {'id': 'option4', 'text': question.option4}
            ]
        }
        for question in questions
    ]

    return render_template('user/attempt_quiz.html', quiz=quiz, questions=serialized_questions, current_question_index=current_question_index)



@user_blueprint.route('instructions/<int:quiz_id>')
def instructions(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz not found!', 'error')
        return redirect(url_for('user.dashboard'))
    return render_template('user/instructions.html', quiz=quiz)