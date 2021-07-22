from flask import render_template, request, Blueprint, flash, redirect, url_for, current_app, session, g
from datetime import datetime
from flask_login import login_required, current_user
from app.models import Score, Contact
from app import db
from app.main.utils import trivia, answer_choices, get_trivia_api_latest_resp, \
    evaluate_trivia_response
from app.main.riddle_utils import riddle_of_the_hour, eval_rod, get_riddle_h_u_ans_recent, \
    get_riddle_h_u_ans_max_tup, post_riddle_h_u_ans, post_riddle_h_tup, get_past_riddles
from app.main.trivia_dash import user_perf_trivia_dash, leaderboard_trivia_dash
from app.main.forms import RodForm
from datetime import timedelta
import uuid
import html


main = Blueprint('main', __name__)


# define the session timeout
@main.before_request
def before_request():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(minutes=30)
    session.modified = True
    g.user = current_user


@main.route('/', methods=["GET", "POST"])
@main.route("/index.html", methods=["GET", "POST"])
def index():
    return render_template("/public/main-page/index.html",
                           today_date=datetime.now().strftime("%d-%B-%Y"),
                           trivia=trivia(),
                           rod=riddle_of_the_hour(),
                           rod_ans_recent=get_riddle_h_u_ans_recent(),
                           rod_ans_tup=get_riddle_h_u_ans_max_tup(),
                           past_riddles=get_past_riddles(),
                           form=RodForm(),
                           user=current_user,
                           score=user_perf_trivia_dash(),
                           lb=leaderboard_trivia_dash(),
                           choice=answer_choices(),
                           title='RTB | Brainy Fun',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])


@main.route("/trivia-result", methods=["GET", "POST"])
def trivia_result():
    user_answer = request.form["answer"]
    res = evaluate_trivia_response(user_answer)
    trivia_response = get_trivia_api_latest_resp()

    return render_template("/public/main-page/trivia-result.html",
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


@main.route("/next-trivia", methods=["GET", "POST"])
def next_trivia():
    session['NEXT_TRIVIA_FLAG'] = True
    return render_template("/public/main-page/trivia-quiz.html",
                           today_date=datetime.now().strftime("%d-%B-%Y"),
                           trivia=trivia(),
                           user=current_user,
                           score=user_perf_trivia_dash(),
                           lb=leaderboard_trivia_dash(),
                           choice=answer_choices(),
                           title='RTB | Brainy Fun',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])


@main.route("/post-riddle-answer", methods=["GET", "POST"])
def post_riddle_ans():
    form = RodForm()
    user_ans = form.rod_user_ans.data
    post_riddle_h_u_ans(user_ans)
    return redirect(url_for('main.index'))


@main.route("/post-riddle-tup", methods=["GET", "POST"])
def post_riddle_tup():
    if request.method == "POST":
        post_riddle_h_tup(request.form.get('tstamp'), request.form.get('user_name'))
    return redirect(url_for('main.index'))