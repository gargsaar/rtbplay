from app import db
import requests
from flask_login import current_user
from sqlalchemy import text
from app.models import RiddleOfTheHour, RiddleOfTheHourUserAnswer
from flask import redirect, url_for, flash
import uuid
import json
import re
import time


# get riddle of the day from the database
def riddle_of_the_hour():
    # fetch rod from the database (remember: rod_id datatype is string in the database)
    sql_query = text('select count(*) from riddle_of_the_hour;')
    rod_response = db.engine.execute(sql_query).fetchall()

    # read counter value from counter.txt which is updated daily via cron job
    filename = 'counter.txt'
    with open(filename) as fh:
        for line in fh:
            counter = line

    if counter == rod_response[0][0]:
        # reset the counter and write into counter.txt
        counter = 1
        with open(filename, 'w') as f:
            f.write(counter)

    # fetch rod from the database (remember: rod_id datatype is string in the database)
    sql_query = text('select * from riddle_of_the_hour where (rod_id=:c);')
    rod_response = db.engine.execute(sql_query, c=counter).fetchall()

    return rod_response[0]


# evaluate user's answer for riddle of the day
def eval_rod(rod_user_answer):
    res = 'incorrect'
    pattern = riddle_of_the_day()[2].lower()
    user_text = rod_user_answer.lower().split()
    for i in user_text:
        if re.search(i, pattern):
            res = 'correct'
    return res


def get_riddle_h_u_ans_recent():
    # fetch rod from the database (remember: rod_id datatype is string in the database)
    sql_query = text('select * from riddle_of_the_hour_user_answer ORDER BY answer_posted_at DESC LIMIT 1;')
    response = db.engine.execute(sql_query).fetchall()
    return response[0]


def get_riddle_h_u_ans_max_tup():
    # fetch rod from the database (remember: rod_id datatype is string in the database)
    sql_query = text('select * from riddle_of_the_hour_user_answer ORDER BY thumbsup_count DESC; ')
    response = db.engine.execute(sql_query).fetchall()
    return response


def post_riddle_h_u_ans(user_ans):
    # read counter value from counter.txt which is updated daily via cron job
    filename = 'counter.txt'
    with open(filename) as fh:
        for line in fh:
            counter = line

    if current_user.is_authenticated:
        user_name = current_user.username
    else:
        user_name = "anonymous_user"

    new_u_answer = RiddleOfTheHourUserAnswer(
        id=str(uuid.uuid1()),
        rod_id=str(counter),
        rod_user_ans=user_ans,
        username=user_name,
        thumbsup_count="0"
    )
    db.session.add(new_u_answer)
    db.session.commit()

    flash(f"Thank you for posting your answer! A big Thumbs Up to you :).", 'success')

    return redirect(url_for('main.index'))


def get_past_riddles():
    # read counter value from counter.txt which is updated daily via cron job
    filename = 'counter.txt'
    with open(filename) as fh:
        for line in fh:
            counter = line

    # fetch rod from the database (remember: rod_id datatype is string in the database)
    sql_query = text('select * from riddle_of_the_hour where rod_id IN (:r1, :r2, :r3);')
    response = db.engine.execute(sql_query, r1=str(int(counter)-1), r2=str(int(counter)-2), r3=str(int(counter)-3)).fetchall()
    return response


def post_riddle_h_tup(tstamp, user_name):
    # get thumbsup count from database for the specific row record
    sql_query = text('select thumbsup_count from riddle_of_the_hour_user_answer '
                     'where (answer_posted_at=:t) and (username=:u);')
    tup_count = db.engine.execute(sql_query, t=tstamp, u=user_name).fetchall()
    tup_count = int(tup_count[0][0]) + 1

    # post increment thumbsup count into the specific row record
    sql_query = text('update riddle_of_the_hour_user_answer set thumbsup_count=:c '
                     'where (answer_posted_at=:t) and (username=:u);')
    db.engine.execute(sql_query, t=tstamp, u=user_name, c=tup_count)

    flash(f'Thumbs Up to you! Thank you for your response :).', 'success')

    return redirect(url_for('main.index'))