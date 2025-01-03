from flask import Flask, jsonify ,render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

app = Flask(__name__)

db = SQLAlchemy
DB_NAME = "database.db"

def create_app():
    app.config['SECRET_KEY'] = "quizmaster"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    return app
