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

# # Save response route for "Save and Next"
# @user_blueprint.route('/save_response', methods=['POST'])
# def save_response():
#     user_id = session.get('user_id')
#     if not user_id:
#         return jsonify({'error': 'You must be logged in to save responses.'}), 403

#     data = request.get_json()
#     quiz_id = data.get('quiz_id')
#     question_id = data.get('question_id')
#     selected_answers = data.get('answers', [])

#     # Check if this user has already attempted this question
#     existing_attempt = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id, question_id=question_id).first()

#     if not existing_attempt:
#         # Create new attempt entries for each selected answer
#         for answer in selected_answers:
#             attempt = QuizAttempt(
#                 user_id=user_id,
#                 quiz_id=quiz_id,
#                 question_id=question_id,
#                 answer=answer,
#                 attempt_date=datetime.now()
#             )
#             db.session.add(attempt)
#     else:
#         # Update existing attempt
#         QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id, question_id=question_id).delete()
#         for answer in selected_answers:
#             attempt = QuizAttempt(
#                 user_id=user_id,
#                 quiz_id=quiz_id,
#                 question_id=question_id,
#                 answer=answer,
#                 attempt_date=datetime.now()
#             )
#             db.session.add(attempt)

#     db.session.commit()
#     return jsonify({'message': 'Response saved successfully.'})



# # Attempt Quiz Route
# @user_blueprint.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
# def attempt_quiz(quiz_id):
#     quiz = Quiz.query.get_or_404(quiz_id)
#     questions = Question.query.filter_by(quiz_id=quiz_id).all()
#     user_id = session.get('user_id')

#     if request.method == 'POST':
#         # Check if quiz already attempted
#         if quiz.is_attempted_by_user(user_id):
#             flash('You have already attempted this quiz.', 'error')
#             return redirect(url_for('dashboard'))

#         # Process and save all quiz responses
#         answers = request.form.to_dict(flat=False)
#         for question_id, answer_list in answers.items():
#             if question_id.startswith('q'):
#                 question_id = int(question_id[1:])
#                 for answer in answer_list:
#                     attempt = QuizAttempt(
#                         user_id=user_id,
#                         quiz_id=quiz_id,
#                         question_id=question_id,
#                         answer=answer,
#                         attempt_date=datetime.now()
#                     )
#                     db.session.add(attempt)

#         # Mark quiz as attempted
#         quiz.status = 'attempted'
#         db.session.commit()

#         flash('Quiz submitted successfully!', 'success')
#         return redirect(url_for('dashboard'))

#     current_question_index = 0  # Initialize the current question index
#     return render_template('user/attempt_quiz.html', quiz=quiz, questions=questions, current_question_index=current_question_index)

@user_blueprint.route('/save_response', methods=['POST'])
def save_response():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'You must be logged in to save responses.'}), 403

    data = request.get_json()
    quiz_id = data.get('quiz_id')
    question_id = data.get('question_id')
    selected_answers = data.get('answers', [])

    # Check if this user has already attempted this question
    existing_attempt = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id, question_id=question_id).first()

    if not existing_attempt:
        # Create new attempt entries for each selected answer
        for answer in selected_answers:
            attempt = QuizAttempt(
                user_id=user_id,
                quiz_id=quiz_id,
                question_id=question_id,
                answer=answer,
                attempt_date=datetime.now()
            )
            db.session.add(attempt)
    else:
        # Update existing attempt
        db.session.query(QuizAttempt).filter_by(user_id=user_id, quiz_id=quiz_id, question_id=question_id).delete()
        for answer in selected_answers:
            attempt = QuizAttempt(
                user_id=user_id,
                quiz_id=quiz_id,
                question_id=question_id,
                answer=answer,
                attempt_date=datetime.now()
            )
            db.session.add(attempt)

    db.session.commit()
    return jsonify({'message': 'Response saved successfully.'})



@user_blueprint.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to attempt the quiz.', 'error')
        return redirect(url_for('auth.user_login'))

    # Check if the user has already attempted this quiz
    existing_attempt = Result.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if existing_attempt:
        flash('You have already attempted this quiz.', 'info')
        return redirect(url_for('user.dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        answers = request.form.to_dict(flat=False)  # Get all answers from the form
        total_questions = len(questions)
        correct_answers = 0
        wrong_answers = 0
        attempted_questions = 0

        # Loop through all questions
        for question in questions:
            question_id = question.id
            selected_answer = answers.get(f'q{question_id}', [])  # Get user's answer for this question

            # Save each answer in QuizAttempt
            if selected_answer:  # If an answer was provided
                for answer in selected_answer:
                    attempt = QuizAttempt(
                        user_id=user_id,
                        quiz_id=quiz_id,
                        question_id=question_id,
                        answer=answer,
                        attempt_date=datetime.now()
                    )
                    db.session.add(attempt)

                # Compare with the correct answer
                correct_option = question.correct_options.split(',')  # Handle multiple correct options
                if set(selected_answer) == set(correct_option):
                    correct_answers += 1
                else:
                    wrong_answers += 1
                attempted_questions += 1

        # Calculate skipped questions
        skipped_questions = total_questions - attempted_questions

        # Save result
        result = Result(
            user_id=user_id,
            quiz_id=quiz_id,
            score=correct_answers,  # Assuming 1 point per correct answer
            total_questions=total_questions,
            attempted_questions=attempted_questions,
            correct_answers=correct_answers,
            wrong_answers=wrong_answers,
            skipped_questions=skipped_questions,
            status='attempted'
        )
        quiz.status = 'attempted'  # Mark the quiz as attempted
        db.session.add(result)
        db.session.commit()

        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('user.dashboard'))

    # Render questions for the quiz
    serialized_questions = [
        {
            'id': question.id,
            'title': question.title,
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

    current_question_index = 0  # Initialize the current question index
    return render_template(
        'user/attempt_quiz.html', 
        quiz=quiz, 
        questions=serialized_questions,
        current_question_index=current_question_index
    )







# @user_blueprint.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
# def attempt_quiz(quiz_id):
#     quiz = Quiz.query.get_or_404(quiz_id)
#     questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
#     if request.method == 'POST':
#         user_id = session.get('user_id')
#         if not user_id:
#             flash('You must be logged in to attempt the quiz.', 'error')
#             return redirect(url_for('auth.user_login'))

#         # Retrieve user's answers from the form
#         answers = request.form.to_dict(flat=False)

#         # Save the quiz attempt
#         for question_id, answer_list in answers.items():
#             if question_id.startswith('q'):
#                 question_id = int(question_id[1:])
#                 for answer in answer_list:
#                     attempt = QuizAttempt(
#                         user_id=user_id,
#                         quiz_id=quiz_id,
#                         question_id=question_id,
#                         answer=answer,
#                         attempt_date=datetime.now()
#                     )
#                     db.session.add(attempt)

#         db.session.commit()
#         flash('Quiz attempt saved successfully!', 'success')
#         return redirect(url_for('user.dashboard'))

#     current_question_index = 0  # Initialize the current question index

#     # Serialize questions to JSON-compatible format
#     serialized_questions = [
#         {
#             'id': question.id,
#             'text': question.text,
#             'type': question.type,
#             'options': [
#                 {'id': f'option{i+1}', 'text': option}
#                 for i, option in enumerate([question.option1, question.option2, question.option3, question.option4])
#                 if option  # Include only non-empty options
#             ]
#         }
#         for question in questions
#     ]

#     return render_template('user/attempt_quiz.html', quiz=quiz, questions=serialized_questions, current_question_index=current_question_index)



@user_blueprint.route('instructions/<int:quiz_id>')
def instructions(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz not found!', 'error')
        return redirect(url_for('user.dashboard'))
    return render_template('user/instructions.html', quiz=quiz)