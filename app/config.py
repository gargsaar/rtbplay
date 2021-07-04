import os
import requests


def trivia_session_token():
    token_json = requests.get('https://opentdb.com/api_token.php?command=request').json()
    return token_json["token"]


class Config(object):
    # app secret token
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # external api keys
    GENDER_API_KEY = os.environ.get('GENDER_API_KEY')
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
    MAILBOXLAYER_API_KEY = os.environ.get('MAILBOXLAYER_API_KEY')
    TRIVIA_SESSION_TOKEN = trivia_session_token()

    SESSION_COOKIE_SECURE = True


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True

    # mailserver config
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')


class TestingConfig(Config):
    TESTING = True