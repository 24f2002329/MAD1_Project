# from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from app import db
# from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # password_hash = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # Default role is 'user'
    full_name = db.Column(db.String(150), nullable=True)
    dob = db.Column(db.Date, nullable=True)

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_date = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_options = db.Column(db.String(200), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    negative_marks = db.Column(db.Integer, nullable=False)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)  # Ensure this line is present
    answer = db.Column(db.String(200), nullable=False)
    attempt_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quiz = db.relationship('Quiz', backref='quiz_attempts', lazy=True)
    user = db.relationship('User', backref='quiz_attempts', lazy=True)
    question = db.relationship('Question', backref='quiz_attempts', lazy=True)



class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    attempted_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    wrong_answers = db.Column(db.Integer, nullable=False)
    skipped_questions = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref='result', lazy=True)
    quiz = db.relationship('Quiz', backref='result', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
