from flask import Blueprint, render_template, request, redirect, url_for, flash, session, redirect
from app.models.models import db, User, Subject, Chapter, Quiz, Question

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
    return render_template('admin/quiz.html')

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