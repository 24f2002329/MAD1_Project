from flask import Flask, jsonify ,render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_migrate import Migrate
from .models.models import User, db

app = Flask(__name__)

migrate = Migrate(app, db)
DB_NAME = "database.db"

def create_app():
    app.config['SECRET_KEY'] = "quizmaster"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from .routes.auth import auth_blueprint
    from .routes.user import user_blueprint
    from .routes.admin import admin_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(admin_blueprint)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    

    @app.route('/')
    def home():
        return render_template('index.html')
    

    login_manager = LoginManager()
    login_manager.init_app(app)

    from .models.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    return app
