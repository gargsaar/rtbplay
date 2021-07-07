from flask import render_template, request, Blueprint, flash, redirect, url_for
from datetime import datetime
from flask_login import login_required, current_user
from app.models import Score, Contact
from app import db
from app.main.utils import trivia, answer_choices, get_trivia_api_latest_resp, evaluate_trivia_response
from app.main.dash import user_perf_trivia_dash, leaderboard_trivia_dash
import uuid
import html


main = Blueprint('main', __name__)


@main.route("/index.html", methods=["GET", "POST"])
@login_required
def index():
    return render_template("/public/main-page/index.html",
                           today_date=datetime.now().strftime("%d-%B-%Y"),
                           trivia=trivia(),
                           user=current_user,
                           score=user_perf_trivia_dash(),
                           lb=leaderboard_trivia_dash(),
                           choice=answer_choices(),
                           title='RTB | Brainy Fun',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])


@main.route("/result", methods=["GET", "POST"])
@login_required
def result():
    user_answer = request.form["answer"]
    res = evaluate_trivia_response(user_answer)
    trivia_response = get_trivia_api_latest_resp()

    return render_template("/public/main-page/result.html",
                           value=res,
                           trivia=trivia_response,
                           today_date=datetime.now().strftime("%d-%B-%Y"),
                           user=current_user,
                           score=user_perf_trivia_dash(),
                           lb=leaderboard_trivia_dash(),
                           user_answer=user_answer,
                           title='RTB | Brainy Fun',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])







