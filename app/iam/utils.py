from flask import current_app, url_for
import requests
from flask_mail import Message
from app import mail


def gender_prediction(first_name):
    response = requests.get(
        f"https://gender-api.com/get-country-of-origin?name={first_name}&key={current_app.config['GENDER_API_KEY']}").json()
    return response


def email_validation(user_email):
    response = requests.get(
        f"https://apilayer.net/api/check?access_key={current_app.config['MAILBOXLAYER_API_KEY']}"
        f"&email={user_email}").json()
    return response


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
                    {url_for('iam.reset_token', token=token, _external=True)}
                    If you did not make this request then simply ignore this email 
                    and no changes will be made.
                '''
    mail.send(msg)


