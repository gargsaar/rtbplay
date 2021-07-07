from app import db
import requests
from flask_login import current_user
from sqlalchemy import text
import random
from flask import current_app
import html
from app.models import Score, TriviaApiResponse
import uuid


def get_trivia_api_latest_resp():
    sql_query = text('SELECT * FROM trivia_api_response ORDER BY created_at DESC LIMIT 1;')
    trivia_response = db.engine.execute(sql_query).fetchall()
    return trivia_response[0]


def trivia():
    trivia_response = {}
    opentdb_api_url = 'https://opentdb.com/api.php?amount=1&token='
    token = current_app.config['TRIVIA_SESSION_TOKEN']
    response = requests.get(f"{opentdb_api_url}{token}").json()

    trivia_response.update(response)

    if trivia_response["response_code"] == 0:
        new_trivia = TriviaApiResponse(
            username=current_user.username,
            category=html.unescape(trivia_response["results"][0]["category"]),
            type=html.unescape(trivia_response["results"][0]["type"]),
            difficulty=html.unescape(trivia_response["results"][0]["difficulty"]),
            question=html.unescape(trivia_response["results"][0]["question"]),
            correct_answer=html.unescape(trivia_response["results"][0]["correct_answer"]),
            incorrect_answers=html.unescape(trivia_response["results"][0]["incorrect_answers"]),
            trivia_response=str(trivia_response)
        )
        db.session.add(new_trivia)
        db.session.commit()

    else:
        trivia()

    trivia_response = get_trivia_api_latest_resp()

    return trivia_response


def answer_choices():
    ans_choices = []
    trivia_resp = get_trivia_api_latest_resp()

    if trivia_resp[3] == 'multiple':
        ans_choices = [trivia_resp[6],
                       trivia_resp[7][0],
                       trivia_resp[7][1],
                       trivia_resp[7][2]
                       ]
        random.shuffle(ans_choices)
        ans_choices.append("I don't know")

    return ans_choices


def update_user_score(score, res):
    new_score = Score(
        id=str(uuid.uuid1()),
        username=current_user.username,
        score=score,
        topic=get_trivia_api_latest_resp()[2],
        res_reason=res,
        player_id=current_user.id,
        trivia_api_response=str(get_trivia_api_latest_resp())
        )
    db.session.add(new_score)
    db.session.commit()


def evaluate_trivia_response(user_answer):
    correct_answer = get_trivia_api_latest_resp()[6]

    if correct_answer == user_answer:
        result = "correct_answer"
        update_user_score(score=10, res=result)
    elif user_answer == "I don't know":
        result = "not_know"
        update_user_score(score=0, res=result)
    else:
        result = "incorrect_answer"
        update_user_score(score=0, res=result)

    return result




