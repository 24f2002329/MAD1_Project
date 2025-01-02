from flask import Flask
from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    return app
