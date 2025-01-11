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
    results = Result.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/user_dashboard.html', username=session['username'], quizzes=upcoming_quizzes, results=results)


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
        new_password = request.form.get('password')
        if new_password:
            user.password = new_password

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/settings.html', user=user)



@user_blueprint.route('/view_quiz/<int:quiz_id>')
def view_quiz(quiz_id): 
    quiz = Quiz.query.get(quiz_id)
    return render_template('user/view_quiz.html', quiz=quiz)




# Save response route for "Save and Next"
@user_blueprint.route('/save_response', methods=['POST'])
def save_response():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'You must be logged in to save responses.'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data.'}), 400
    quiz_id = data.get('quiz_id')
    question_id = data.get('question_id')
    selected_answers = data.get('answers', [])

    # Check if this user has already attempted this question
    existing_attempt = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id, question_id=question_id).first()

    if not existing_attempt:
        # Create new attempt entry with selected answers as a comma-separated string
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            question_id=question_id,
            answers=','.join(selected_answers),
            attempt_date=datetime.now()
        )
        db.session.add(attempt)
    else:
        # Update existing attempt
        existing_attempt.answers = ','.join(selected_answers)
        existing_attempt.attempt_date = datetime.now()

    db.session.commit()
    return jsonify({'message': 'Response saved successfully.'})



@user_blueprint.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    user_id = session.get('user_id')

    if request.method == 'POST':
        # Check if quiz already attempted
        existing_attempt = Result.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
        if existing_attempt:
            flash('You have already attempted this quiz.', 'error')
            return redirect(url_for('user.dashboard'))

        # Process and save all quiz responses
        answers = request.form.to_dict(flat=False)
        for question in questions:
            question_id = question.id
            selected_answers = answers.get(f'q{question_id}', [])

            if selected_answers:
                # Store selected answers as a comma-separated string
                attempt = QuizAttempt(
                    user_id=user_id,
                    quiz_id=quiz_id,
                    question_id=question_id,
                    answers=','.join(selected_answers),
                    attempt_date=datetime.now()
                )
                db.session.add(attempt)

        db.session.commit()

        # Calculate the result based on QuizAttempt entries
        total_questions = len(questions)
        correct_answers = 0
        wrong_answers = 0
        attempted_questions = 0
        total_score = 0

        for question in questions:
            question_id = question.id
            attempt = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id, question_id=question_id).first()
            if attempt:
                attempted_questions += 1
                selected_answers = attempt.answers.split(',')
                correct_options = question.correct_options.split(',')

                if set(selected_answers) == set(correct_options):
                    correct_answers += 1
                    total_score += question.marks  # Assuming `marks` is the field for correct answer marks
                elif set(selected_answers) == {''}:  # Check if the question was skipped
                    pass
                # Partial marking for partially correct answers
                elif set(selected_answers).issubset(set(correct_options)):
                    partial_score = (question.marks / len(correct_options)) * len(set(selected_answers))
                    total_score += partial_score  # Award partial marks based on the number of correct options selected
                else:
                    wrong_answers += 1
                    total_score -= question.negative_marks  # Assuming `negative_marks` is the field for wrong answer marks

        skipped_questions = total_questions - attempted_questions

        # Save the result
        result = Result(
            user_id=user_id,
            quiz_id=quiz_id,
            score=total_score,
            total_questions=total_questions,
            attempted_questions=attempted_questions,
            correct_answers=correct_answers,
            wrong_answers=wrong_answers,
            skipped_questions=skipped_questions,
            created_at=datetime.now()
        )
        db.session.add(result)

        # Mark quiz as attempted
        quiz.status = 'attempted'
        db.session.commit()

        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('user.dashboard'))

    current_question_index = 0  # Initialize the current question index

    # Serialize questions to JSON-compatible format
    serialized_questions = [
        {
            'id': question.id,
            'text': question.text,
            'type': question.type,
            'options': [
                {'id': f'option{i+1}', 'text': option}
                for i, option in enumerate([question.option1, question.option2, question.option3, question.option4])
                if option  # Include only non-empty options
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