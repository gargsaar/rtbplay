from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from app.config import Config, DevConfig, ProdConfig

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)

    if app.config['ENV'] == 'production':
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)

    db.init_app(app)

    login_manager.init_app(app)
    mail.init_app(app)

    from app.general.routes import general
    from app.handlers.routes import handlers
    from app.iam.routes import iam
    from app.main.routes import main
    from app.profile.routes import profile
    app.register_blueprint(general)
    app.register_blueprint(handlers)
    app.register_blueprint(iam)
    app.register_blueprint(main)
    app.register_blueprint(profile)

    return app





