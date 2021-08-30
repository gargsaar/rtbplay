import os
import requests
import analytics
from apscheduler.schedulers.background import BackgroundScheduler


# cron job function for riddle counter. write into counter.txt via cron job
def riddle_counter_cron():
    filename = 'counter.txt'
    counter = 0
    # read current counter value from counter.txt
    with open(filename) as fh:
        for line in fh:
            counter = int(line)

    counter = str(counter + 1)

    # increment the counter and write into counter.txt
    with open(filename, 'w') as f:
        f.write(counter)


# initialize scheduler with your preferred timezone
scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Calcutta'})
scheduler.add_job(func=riddle_counter_cron, trigger='interval', hours=2)
scheduler.start()


class Config:
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

    SESSION_COOKIE_SECURE = True


class ProdConfig(Config):
    SEGMENT_JS_TRACKING_KEY = os.environ.get('WEBSITE_RTB_PROD_JS_KEY')
    GA_SITE_TAG = os.environ.get('GA_SITE_TAG')
    analytics.write_key = os.environ.get('SEGMENT_RTB_PY_SERVER_PROD_KEY')


class DevConfig(Config):
    SEGMENT_JS_TRACKING_KEY = os.environ.get('WEBSITE_RTB_DEV_JS_KEY')
    GA_SITE_TAG = os.environ.get('GA_SITE_TAG')

    # mailserver config
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
