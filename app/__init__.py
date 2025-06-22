from flask import Flask
from .db import init_db
from flask import session
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'changeme'
    bcrypt.init_app(app)

    init_db()

    from .routes import main
    app.register_blueprint(main)

    return app