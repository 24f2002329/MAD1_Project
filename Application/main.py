from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from QuizMaster.models import db, User, Subject, Chapter, Quiz, Question, Score
from QuizMaster.auth import routes
from QuizMaster import create_app

app = create_app()
if __name__ == '__main__':
    app.run(debug=True)