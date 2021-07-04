from app import db
from flask_login import login_user
from werkzeug.security import check_password_hash
from flask import render_template, flash, redirect, url_for, g, request, Blueprint, session, current_app
from werkzeug.security import generate_password_hash
from flask_login import current_user, logout_user
from app.main.forms import RequestResetForm, ResetPasswordForm
from app.models import Account, APIMetaData
from datetime import timedelta
from app.main.utils import email_validation, gender_prediction, send_reset_email
import uuid


main = Blueprint('main', __name__)


@main.before_request
def before_request():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(minutes=60)
    session.modified = True
    g.user = current_user


@main.route('/', methods=["GET", "POST"])
@main.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = Account.query.filter_by(username=username).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('main.login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('main.login'))
        else:
            login_user(user, remember=False)
            return redirect(url_for('users.index'))

    return render_template("/public/unauthenticated/login.html", title='RTB | Login')


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@main.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        if Account.query.filter_by(email=request.form.get('email')).first():
            # Email already exists
            flash("You've already signed up with that email, log in instead.")
            return redirect(url_for('main.login'))

        if Account.query.filter_by(username=request.form.get('username')).first():
            # Username already exists
            flash("This username is already taken up, use another.")
            return redirect(url_for('main.signup'))

        if email_validation(request.form.get('email'))['score'] < 0.5:
            flash(f"It looks like an invalid email. "
                  f"(Email verification score is low: "
                  f"{email_validation(request.form.get('email'))['score']})")
            return redirect(url_for('main.signup'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        first_name = request.form.get('fname')

        new_user = Account(
            id=str(uuid.uuid1()),
            email=request.form.get('email'),
            username=request.form.get('username'),
            password=hash_and_salted_password,
            first_name=request.form.get('fname'),
            predicted_gender=gender_prediction(first_name)["gender"],
            gender_predict_accuracy=gender_prediction(first_name)["accuracy"],
            predicted_country=gender_prediction(first_name)["country_of_origin"][0]["country"].lower()

        )
        db.session.add(new_user)
        db.session.commit()

        new_api_meta_data = APIMetaData(
            username=request.form.get('username'),
            gender_api_response=str(gender_prediction(first_name)),
            email_api_response=str(email_validation(request.form.get('email')))
        )

        db.session.add(new_api_meta_data)
        db.session.commit()
        login_user(new_user, remember=False)
        return redirect(url_for("users.index"))

    return render_template("/public/unauthenticated/signup.html", title='RTB | Signup')


@main.route("/about", methods=["GET", "POST"])
def about():
    return render_template("/public/unauthenticated/about.html", title='RTB | About')


@main.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Account.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('main.login'))
    return render_template('/public/unauthenticated/reset_request.html',
                           title='Reset Password', form=form)


@main.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.index'))
    user = Account.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('main.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('/public/unauthenticated/reset_token.html',
                           title='Reset Password', form=form)

