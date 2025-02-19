from flask import Flask, jsonify ,render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_migrate import Migrate
from datetime import timedelta
from .filters import register_filters
import os   


app = Flask(__name__)
register_filters(app)

db = SQLAlchemy()
migrate = Migrate()

from .models.models import *


def create_app():
    app.config['SECRET_KEY'] = "quizmaster"

    # Use absolute path for the database
    database_path = os.path.join(app.instance_path, 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Set session timeout to 10 minutes
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'img/question')

    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.before_request
    def refresh_session():
        session.modified = True



    from .routes.auth import auth_blueprint
    from .routes.user import user_blueprint
    from .routes.admin import admin_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route('/')
    def home():
        return render_template('index.html')

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))



    @app.template_filter('int_to_time')
    def int_to_time(minutes):
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02}:{mins:02}"



    return app



