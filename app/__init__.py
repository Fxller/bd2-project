from flask import Flask
from .extensions import mongo
from flask_bcrypt import Bcrypt
from .anime.routes import anime_bp
from .users.routes import users_bp
from .main.routes import main_bp
from dotenv import load_dotenv
import os

bcrypt = Bcrypt()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.secret_key = os.getenv("SECRET_KEY")

    mongo.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(anime_bp, url_prefix="/anime")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(main_bp)

    return app
