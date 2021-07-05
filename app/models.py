from app import db, login_manager
from flask_login import UserMixin, current_user
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import render_template


@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return render_template("/public/unauthenticated/login.html", logged_in=current_user.is_active)



class Account(UserMixin, db.Model):
    id = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    email = db.Column(db.String(60), unique=True, nullable=False)
    first_name = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    predicted_gender = db.Column(db.String(10), nullable=True)
    gender_predict_accuracy = db.Column(db.Integer(), nullable=True, default=50)
    predicted_country = db.Column(db.String(10), nullable=True, default='us')
    scores = db.relationship('Score', backref='player', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Account.query.get(user_id)


class Score(UserMixin, db.Model):
    id = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    score_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    username = db.Column(db.String(30), nullable=False)
    score = db.Column(db.Integer(), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    res_reason = db.Column(db.String(20), nullable=False)
    trivia_api_response = db.Column(db.String(5000), nullable=True)
    player_id = db.Column(db.String(120), db.ForeignKey('account.id'), nullable=False)


class Contact(UserMixin, db.Model):
    message_date = db.Column(db.DateTime, primary_key=True, nullable=False, default=datetime.utcnow)
    email = db.Column(db.String(60), nullable=False)
    message = db.Column(db.String(5000), nullable=False)
    username = db.Column(db.String(30), unique=False, nullable=False)


class APIMetaData(UserMixin, db.Model):
    created_at = db.Column(db.DateTime, primary_key=True, nullable=False, default=datetime.utcnow)
    username = db.Column(db.String(30), unique=False, nullable=False)
    gender_api_response = db.Column(db.String(5000), nullable=False)
    email_api_response = db.Column(db.String(5000), nullable=False)


