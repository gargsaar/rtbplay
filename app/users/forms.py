from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class ContactForm(FlaskForm):
    recaptcha = RecaptchaField()
    email = StringField('Email:', validators=[DataRequired(), Email()])
    message = TextAreaField('Message:', validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField('Send')