from flask import Flask
from config import Config
from .models import db


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from .main import bp
    app.register_blueprint(bp)

    return app
