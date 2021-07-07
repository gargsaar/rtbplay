from app import db
from flask_login import login_user
from werkzeug.security import check_password_hash
from flask import render_template, flash, redirect, url_for, g, request, Blueprint, session, current_app
from werkzeug.security import generate_password_hash
from flask_login import current_user, logout_user
from app.iam.forms import RequestResetForm, ResetPasswordForm
from app.iam.utils import email_validation, gender_prediction, send_reset_email
from app.models import Account, APIMetaData
from datetime import timedelta
import uuid


iam = Blueprint('iam', __name__)


# define the session timeout
@iam.before_request
def before_request():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(minutes=60)
    session.modified = True
    g.user = current_user


# login
@iam.route('/', methods=["GET", "POST"])
@iam.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # get the details from login page
        username = request.form.get('username')
        password = request.form.get('password')
        # get the user credentials from database
        user = Account.query.filter_by(username=username).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('iam.login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('iam.login'))
        else:
            login_user(user, remember=False)
            return redirect(url_for('main.index'))

    return render_template("/public/iam-page/login.html",
                           title='RTB | Login',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])


# logout
@iam.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('iam.login'))


# signup
@iam.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # check in the database if the user email already exists
        if Account.query.filter_by(email=request.form.get('email')).first():
            # flash message if the Email already exists
            flash("You've already signed up with that email, log in instead.")
            return redirect(url_for('main.login'))
        # check in the database if username already exists
        if Account.query.filter_by(username=request.form.get('username')).first():
            # Username already exists
            flash("This username is already taken up, use another.")
            return redirect(url_for('main.signup'))
        # check if the user email is valid using external API from Mailboxlayer
        if email_validation(request.form.get('email'))['score'] < 0.5:
            flash(f"It looks like an invalid email. "
                  f"(Email verification score is low: "
                  f"{email_validation(request.form.get('email'))['score']})")
            return redirect(url_for('main.signup'))
        # encrypt the password to be stored in the database
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        first_name = request.form.get('fname')

        # insert new user's account data into database
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

        # insert new user's gender and email data (generated from external APIs) into database for future reference
        new_api_meta_data = APIMetaData(
            username=request.form.get('username'),
            gender_api_response=str(gender_prediction(first_name)),
            email_api_response=str(email_validation(request.form.get('email')))
            )
        db.session.add(new_api_meta_data)
        db.session.commit()

        # Flask login function to login the user
        login_user(new_user, remember=False)

        return redirect(url_for("main.index"))

    return render_template("/public/iam-page/signup.html",
                           title='RTB | Signup',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])


# reset request
@iam.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    # checking if the user is already logged-in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # rested request form
    form = RequestResetForm()
    if form.validate_on_submit():
        # get user's email id from the database
        user = Account.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')

        return redirect(url_for('iam.login'))

    return render_template('/public/iam-page/reset_request.html',
                           title='Reset Password',
                           form=form,
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])


# reset token
@iam.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # checking if the user is already logged-in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = Account.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('iam.reset_request'))
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

        return redirect(url_for('iam.login'))

    return render_template('/public/iam-page/reset_token.html',
                           title='Reset Password',
                           form=form,
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])

