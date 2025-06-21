from flask import Flask
from .db import init_db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'changeme'

    init_db()

    from .routes import main
    app.register_blueprint(main)

    return app