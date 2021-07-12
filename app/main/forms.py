from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class RodForm(FlaskForm):
    rod_user_ans = StringField('Your Answer:', validators=[DataRequired()])
    submit = SubmitField('Give it a shot')