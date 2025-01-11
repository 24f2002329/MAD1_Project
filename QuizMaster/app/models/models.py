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
    desc = db.Column(db.String(200), nullable=True)
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

    # def is_attempted_by_user(self, user_id):
    #     return QuizAttempt.query.filter_by(user_id=user_id, quiz_id=self.id).count() > 0

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    option1 = db.Column(db.String(200), nullable=True)
    option2 = db.Column(db.String(200), nullable=True)
    option3 = db.Column(db.String(200), nullable=True)
    option4 = db.Column(db.String(200), nullable=True)
    correct_options = db.Column(db.String(200), nullable=False)
    marks = db.Column(db.Integer, nullable=False, default=4)
    negative_marks = db.Column(db.Integer, nullable=False, default=0)
    question_image = db.Column(db.String(200), nullable=True)
    option1_image = db.Column(db.String(200), nullable=True)
    option2_image = db.Column(db.String(200), nullable=True)
    option3_image = db.Column(db.String(200), nullable=True)
    option4_image = db.Column(db.String(200), nullable=True)



class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answers = db.Column(db.String(500), nullable=False)
    attempt_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='quiz_attempts', lazy=True)
    question = db.relationship('Question', backref='quiz_attempts', lazy=True)
    quiz = db.relationship('Quiz', backref='quiz_attempts', lazy=True)

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
    status = db.Column(db.String(20), default='attempted')  # New status field
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='results', lazy=True)
    quiz = db.relationship('Quiz', backref='results', lazy=True)


 





# class QuizAttempt(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
#     answer = db.Column(db.String(200), nullable=False)
#     attempt_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     quiz = db.relationship('Quiz', backref='quiz_attempts', lazy=True)
#     user = db.relationship('User', backref='quiz_attempts', lazy=True)
#     question = db.relationship('Question', backref='quiz_attempts', lazy=True)



# class Result(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
#     score = db.Column(db.Integer, nullable=False)
#     total_questions = db.Column(db.Integer, nullable=False)
#     attempted_questions = db.Column(db.Integer, nullable=False)
#     correct_answers = db.Column(db.Integer, nullable=False)
#     wrong_answers = db.Column(db.Integer, nullable=False)
#     skipped_questions = db.Column(db.Integer, nullable=False)
#     user = db.relationship('User', backref='result', lazy=True)
#     quiz = db.relationship('Quiz', backref='result', lazy=True)
#     created_at = db.Column(db.DateTime, default=datetime.now)
