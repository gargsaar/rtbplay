from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from app.config import Config, DevelopmentConfig, ProductionConfig


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)

    if app.config['ENV'] == 'production':
        app.config.from_object(ProductionConfig)
    elif app.config['ENV'] == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(Config)


    db.init_app(app)

    with app.app_context():
        db.create_all()

    login_manager.init_app(app)
    mail.init_app(app)

    from app.main.routes import main
    from app.users.routes import users
    from app.errors.handlers import errors
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(errors)

    return app





