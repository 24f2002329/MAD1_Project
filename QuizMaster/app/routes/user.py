from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.models.models import *
from datetime import datetime
import matplotlib as plt
import os

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
    upcoming_quizzes = Quiz.query.filter(Quiz.quiz_endtime >= datetime.today()).order_by(Quiz.quiz_date).all()
    past_quizzes = Quiz.query.filter(Quiz.quiz_endtime < datetime.today()).order_by(Quiz.quiz_date.desc()).all()
    results = Result.query.filter_by(user_id=session['user_id']).all()
    now = datetime.now()
    return render_template('user/user_dashboard.html', username=session['username'], quizzes=upcoming_quizzes, results=results, past_quizzes=past_quizzes, now=now)


@user_blueprint.route('/scores')
def scores():
    if 'user_id' not in session:
        return redirect(url_for('auth.user_login'))

    scores = Result.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/scores.html', scores=scores)

@user_blueprint.route('/summary' , methods=['GET', 'POST'])
def summary():
    if 'user_id' not in session:
        return redirect(url_for('auth.user_login'))

    # Generate bar chart for Subject Wise No. of Quizzes
    subjects = list(Subject.query.with_entities(Subject.name).all())
    no_of_quizzes = list(Subject.query.with_entities(Subject.quizzes).all())

    plt.figure(figsize=(8, 8))
    plt.bar(subjects, no_of_quizzes, color='skyblue')
    plt.xlabel('Subjects')
    plt.ylabel('No. of Quizzes')
    plt.title('Subject Wise No. of Quizzes')
    bar_chart_path = os.path.join('static', 'images', 'subject_chart.png')
    plt.savefig(bar_chart_path)
    plt.close()
    

    # Generate pie chart for Subject Wise User Attempts
    quizzes = ['Quiz 1', 'Quiz 2', 'Quiz 3', 'Quiz 4']
    scores = [85, 90, 75, 80]

    plt.figure(figsize=(8, 8))
    plt.pie(scores, labels=quizzes, autopct='%1.1f%%', startangle=140)
    plt.title('Quiz Wise Score')
    pie_chart_path = os.path.join('static', 'images', 'quiz_chart.png')
    plt.savefig(pie_chart_path)
    plt.close()

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



@user_blueprint.route('quiz_score/<int:quiz_id>')
def quiz_score(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz not found!', 'error')
        return redirect(url_for('user.dashboard'))
    
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to view quiz scores.', 'error')
        return redirect(url_for('auth.user_login'))
    
    result = Result.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not result:
        flash('Quiz not attempted yet.', 'error')
        return redirect(url_for('user.dashboard'))
    
    quiz_data = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id).all()
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    return render_template('user/quiz_score.html', quiz=quiz, result=result, quiz_data=quiz_data, questions=questions)


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
        partially_correct_answers = 0
        total_marks_quiz = 0

        for question in questions:
            total_marks_quiz += question.marks
            question_id = question.id
            attempt = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id, question_id=question_id).first()
            if attempt and attempt.answers:
                attempted_questions += 1
                selected_answers = attempt.answers.split(',')
                for i,x in enumerate(selected_answers):
                    option = x.replace("option", "")
                    selected_answers[i] = option
                correct_options = question.correct_options.split(',')

                if set(selected_answers) == set(correct_options):
                    correct_answers += 1
                    total_score += question.marks  # Assuming `marks` is the field for correct answer marks
                elif set(selected_answers) == {''}:  # Check if the question was skipped
                    pass
                # Partial marking for partially correct answers
                elif set(selected_answers).issubset(set(correct_options)):
                    partially_correct_answers += 1
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
            partially_correct_answers=partially_correct_answers,
            wrong_answers=wrong_answers,
            skipped_questions=skipped_questions,
            created_at=datetime.now(),
            total_marks_quiz = total_marks_quiz
        )
        db.session.add(result)
        db.session.commit()

        flash('Quiz submitted successfully!', 'success')
        return redirect(url_for('user.quiz_score', quiz_id=quiz_id))

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




@user_blueprint.route('/save_timer', methods=['POST'])
def save_timer():
    data = request.get_json()
    remaining_time = data.get('remainingTime')
    user_id = session.get('user_id')  # Assuming you have user sessions

    if user_id:
        timer_db[user_id] = {
            'remaining_time': remaining_time,
            'timestamp': datetime.utcnow()
        }
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

@user_blueprint.route('/get_timer', methods=['GET'])
def get_timer():
    user_id = session.get('user_id')  # Assuming you have user sessions

    if user_id and user_id in timer_db:
        timer_data = timer_db[user_id]
        return jsonify({'remainingTime': timer_data['remaining_time']}), 200
    return jsonify({'remainingTime': None}), 200
