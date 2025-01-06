from flask import Blueprint, render_template, request, redirect, url_for, flash, session, redirect
from app.models.models import *
from datetime import datetime

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')


@admin_blueprint.route('/')
def index():
    if session.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))



@admin_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hardcoded admin credentials
        hardcoded_username = 'admin'
        hardcoded_password = 'devendra'  # In a real application, use a hashed password
        
        if username == hardcoded_username and password == hardcoded_password:
            session['user_id'] = 0  # Assuming the admin user ID is 0
            session['role'] = 'admin'
            session['username'] = hardcoded_username
            flash('Login successful, Hello Admin!', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials. Please try again.', 'error')

    return render_template('admin_login.html')




@admin_blueprint.route('/dashboard', methods=['GET'])
def dashboard():
    if session.get('role') != 'admin':
        return "Unauthorized", 403
    subjects = Subject.query.all()
    
    return render_template('admin/admin_dashboard.html', subjects=subjects)

@admin_blueprint.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    if request.method == 'POST':
        name = request.form['subject']
        subject = Subject(name=name)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully.', 'success')
        return redirect(url_for('admin.add_subject'))

    subjects = Subject.query.all()
    return render_template('admin/add_subject.html', subjects=subjects)


@admin_blueprint.route('/quiz')
def quiz():
    if session.get('role') != 'admin':
        return "Unauthorized", 403
    quizzes = Quiz.query.all()
    subject = Subject.query.all()
    return render_template('admin/quiz.html' , quizzes=quizzes, subject=subject)

@admin_blueprint.route('/summary')
def summary():
    if session.get('role') != 'admin':
        return "Unauthorized", 403
    return render_template('admin/summary.html')


@admin_blueprint.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login')) 



@admin_blueprint.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    subject = Subject.query.get_or_404(subject_id)
    
    # Delete dependent chapters
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    for chapter in chapters:
        db.session.delete(chapter)
    
    db.session.delete(subject)
    db.session.commit()
    flash('Subject and its dependent chapters deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_blueprint.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    chapter = Chapter.query.get_or_404(chapter_id)  # Fetch full chapter object
    if request.method == 'POST':
        chapter.name = request.form['chapter']  # Updated to match template form input
        db.session.commit()
        flash('Chapter updated successfully.', 'success')
        return redirect(url_for('admin.dashboard', subject_id=chapter.subject_id))

    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('admin/edit_chapter.html', chapter=chapter, quizzes=quizzes)




@admin_blueprint.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    chapter = Chapter.query.get_or_404(chapter_id)

    # Delete dependent quizzes
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    for quiz in quizzes:
        db.session.delete(quiz)

    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard', subject_id=chapter.subject_id))




@admin_blueprint.route('/add_chapter/<int:subject_id>', methods=['GET', 'POST'])
def add_chapter(subject_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    if request.method == 'POST':
        name = request.form['chapter']
        chapter = Chapter(name=name, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully.', 'success')
        return redirect(url_for('admin.add_chapter', subject_id=subject_id))

    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/add_chapter.html', subject=subject, chapters=chapters)


@admin_blueprint.route('/create_quiz/', methods=['GET', 'POST'])
def create_quiz():
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    if request.method == 'POST':
        quiz_date = request.form['quiz_date']

        # Convert quiz_date to datetime object
        try:
            quiz_date = datetime.strptime(quiz_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format!', 'error')
            return redirect(url_for('admin.create_quiz', chapter_id=chapter_id))

        chapter = request.form['chapter']
        duration = request.form['quiz_duration']
        chapter_id = Chapter.query.filter_by(name=chapter).first().id
        quiz = Quiz(quiz_date=quiz_date, chapter_id=chapter_id, duration=duration, quiz_chapter=chapter)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully.', 'success')
        return redirect(url_for('admin.create_quiz', chapter_id=chapter_id))

    chapter = Chapter.query.all()
    return render_template('admin/create_quiz.html', chapters=chapter)



@admin_blueprint.route('/add_quiz/<int:chapter_id>', methods=['GET', 'POST'])
def add_quiz(chapter_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    if request.method == 'POST':
        name = request.form['quiz']
        quiz = Quiz(name=name, chapter_id=chapter_id)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully.', 'success')
        return redirect(url_for('admin.add_quiz', chapter_id=chapter_id))

    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('admin/add_quiz.html', chapter=chapter, quizzes=quizzes)


@admin_blueprint.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully.', 'success')
    return redirect(url_for('admin.add_quiz', chapter_id=quiz.chapter_id))


@admin_blueprint.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch full quiz object
    if request.method == 'POST':
        # Convert quiz_date to a date object
        quiz_date_str = request.form['quiz_date']
        quiz.quiz_date = datetime.strptime(quiz_date_str, '%Y-%m-%d').date()
        quiz.duration = request.form['quiz_duration']
        chapter = request.form['chapter']
        quiz.chapter_id = Chapter.query.filter_by(name=chapter).first().id
        db.session.commit()
        flash('Quiz updated successfully.', 'success')
        return redirect(url_for('admin.edit_chapter', chapter_id=quiz.chapter_id))
    chapters = Chapter.query.all() 
    return render_template('admin/edit_quiz.html', quiz=quiz, chapters=chapters)


@admin_blueprint.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    if request.method == 'POST':
        text = request.form['question']
        question = Question(text=text, quiz_id=quiz_id)
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully.', 'success')
        return redirect(url_for('admin.add_question', quiz_id=quiz_id))

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin/add_question.html', quiz=quiz, questions=questions)


@admin_blueprint.route('/delete_question/<int:question_id>')
def delete_question(question_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully.', 'success')
    return redirect(url_for('admin.add_question', quiz_id=question.quiz_id))


@admin_blueprint.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    question = Question.query.get_or_404(question_id)  # Fetch full question object
    if request.method == 'POST':
        question.text = request.form['question']  # Updated to match template form input
        db.session.commit()
        flash('Question updated successfully.', 'success')
        return redirect(url_for('admin.add_question', quiz_id=question.quiz_id))
    
    return render_template('admin/edit_question.html', question=question)


@admin_blueprint.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    subject = Subject.query.get_or_404(subject_id)  # Fetch full subject object
    if request.method == 'POST':
        subject.name = request.form['subject']  # Updated to match template form input
        db.session.commit() # Save changes to the database
        flash('Subject updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_subject.html', subject=subject)

