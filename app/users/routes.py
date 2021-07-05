from flask import render_template, request, Blueprint, flash, redirect, url_for
from datetime import datetime
from flask_login import login_required, current_user
from app.models import Score, Contact
from app import db
from app.users.utils import trivia, trivia_response, answer_choices
from app.users.dash import user_performance, leaderboard
import uuid
from app.users.forms import ContactForm
import html


users = Blueprint('users', __name__)


@users.route("/index.html", methods=["GET", "POST"])
@login_required
def index():
    return render_template("/public/index.html",
                           today_date=datetime.now().strftime("%d-%B-%Y"),
                           trivia=trivia(),
                           user=current_user,
                           score=user_performance(),
                           lb=leaderboard(),
                           choice=answer_choices(),
                           title='RTB | Brainy Fun')


@users.route("/result", methods=["GET", "POST"])
@login_required
def result():
    user_answer = request.form["answer"]
    correct_answer = html.unescape(trivia_response["results"][0]["correct_answer"])
    ques_category = trivia_response["results"][0]["category"]
    trivia_resp_composite = str(trivia_response)[:-1]+",'user_answer':"+user_answer+"}"
    if user_answer == correct_answer:
        res = "Correct"
        new_score = Score(
            id=str(uuid.uuid1()),
            username=current_user.username,
            score=10,
            topic=ques_category,
            res_reason=res,
            player_id=current_user.id,
            trivia_api_response=trivia_resp_composite)
    elif user_answer == "I don't know":
        res = "not_know"
        new_score = Score(
            id=str(uuid.uuid1()),
            username=current_user.username,
            score=0,
            topic=ques_category,
            res_reason=res,
            player_id=current_user.id,
            trivia_api_response=trivia_resp_composite)
    else:
        res = "Incorrect"
        new_score = Score(
            id=str(uuid.uuid1()),
            username=current_user.username,
            score=0,
            topic=ques_category,
            res_reason=res,
            player_id=current_user.id,
            trivia_api_response=trivia_resp_composite)

    db.session.add(new_score)
    db.session.commit()

    return render_template("/public/result.html",
                           value=res,
                           trivia=trivia_response,
                           today_date=datetime.now().strftime("%d-%B-%Y"),
                           user=current_user,
                           score=user_performance(),
                           lb=leaderboard(),
                           user_answer=user_answer,
                           title='RTB | Brainy Fun')


@users.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("/public/errors/page-wip.html",
                           user=current_user,
                           title='RTB | Brainy Fun')


@users.route('/contact', methods=["GET", "POST"])
@login_required
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        flash(f'Message sent. Thank you for reaching out!', 'success')

        # send data to database
        new_message = Contact(
            username=current_user.username,
            email=form.email.data,
            message=form.message.data)

        db.session.add(new_message)
        db.session.commit()

        return redirect(url_for('users.index'))

    return render_template("/public/unauthenticated/contact.html",
                           user=current_user,
                           today_date=datetime.now().strftime("%d-%B-%Y"),
                           form=form,
                           title='RTB | Contact')
