from app import db
import requests
from flask_login import current_user
from sqlalchemy import text
import random
from flask import current_app, session
import html
from app.models import Score, TriviaApiResponse
import uuid
import json
import re
import time
import analytics


def get_trivia_api_latest_resp():
    sql_query = text('SELECT * FROM trivia_api_response ORDER BY created_at DESC LIMIT 1;')
    trivia_response = db.engine.execute(sql_query).fetchall()
    return trivia_response[0]


def set_trivia_api_resp():
    trivia_response = {}
    opentdb_api_url = 'https://opentdb.com/api.php?amount=1&token='

    # generate new token for trivia api and save in session
    if 'TRIVIA_SESSION_TOKEN' not in session:
        token_json = requests.get('https://opentdb.com/api_token.php?command=request').json()
        session['TRIVIA_SESSION_TOKEN'] = token_json["token"]

    response = requests.get(f"{opentdb_api_url}{session['TRIVIA_SESSION_TOKEN']}").json()
    trivia_response.update(response)

    if current_user.is_authenticated:
        user_name = current_user.username
    else:
        user_name = "anonymous_user"

    if trivia_response["response_code"] == 0:
        new_trivia = TriviaApiResponse(
            username=user_name,
            category=html.unescape(trivia_response["results"][0]["category"]),
            type=html.unescape(trivia_response["results"][0]["type"]),
            difficulty=html.unescape(trivia_response["results"][0]["difficulty"]),
            question=html.unescape(trivia_response["results"][0]["question"]),
            correct_answer=html.unescape(trivia_response["results"][0]["correct_answer"]),
            incorrect_answers=trivia_response["results"][0]["incorrect_answers"],
            trivia_response=str(trivia_response)
        )
        db.session.add(new_trivia)
        db.session.commit()
    else:
        trivia()

    return None


def trivia():
    # set the next riddle flag as a session variable
    if 'NEXT_TRIVIA_FLAG' not in session:
        set_trivia_api_resp()
        session['NEXT_TRIVIA_FLAG'] = False

    if session['NEXT_TRIVIA_FLAG']:
        set_trivia_api_resp()
        session['NEXT_TRIVIA_FLAG'] = False

    trivia_response = get_trivia_api_latest_resp()

    return trivia_response


def answer_choices():
    ans_choices = []
    trivia_resp = get_trivia_api_latest_resp()

    if trivia_resp[3] == 'multiple':
        ans_choices = [trivia_resp[6],
                       html.unescape(trivia_resp[7][0]),
                       html.unescape(trivia_resp[7][1]),
                       html.unescape(trivia_resp[7][2])
                       ]
        random.shuffle(ans_choices)
        ans_choices.append("I don't know")

    return ans_choices


def update_user_score(score, res):

    if current_user.is_authenticated:
        user_name = current_user.username
        player = current_user.id
    else:
        user_name = "anonymous_user"
        player = "12345"

    new_score = Score(
        id=str(uuid.uuid1()),
        username=user_name,
        score=score,
        topic=get_trivia_api_latest_resp()[2],
        res_reason=res,
        player_id=player,
        trivia_api_response=str(get_trivia_api_latest_resp())
        )
    db.session.add(new_score)
    db.session.commit()


def evaluate_trivia_response(user_answer):
    giphy_correct = ['SScSc0nO2tezJNQc21', 'QsnJkPUPi7ZThgC0AF', 'jokQb79w49Tea3pjFz', 'oOCbcGBJjlXJL8imGO',
                     'l0MYKDrj6SXHz8YYU', 'dXckBa1HDG86RqUh19', 'xlMWh89tib67i2jSJO', 'ABhl0oGBxJ8Z7gAuYo']
    giphy_notknow = ['J1YFTAeTT3UAxnl6Bx', 'U2MDh3POLyBGqxEGln', '1kenyYNFG9wTUyHMjk', '24FVIYV226vScTh3Sn',
                     'ijxKTF6iE4K4M', '6NVOQr1I5H1MA', 'rdEE8wlaB5ngr5o2rZ', 'VhPrja0yLYBrm7WP4P']
    giphy_incorrect = ['xVIkfXYGTJeZKilg3p', 'Wq9RLX06zRg4UM42Qf', 'dDYfbIf66nwwl8uphc', '2UFSNhXNhmQBoMwV5T',
                       'S4BDGxHKIB6nW9PiyA', 'xT5LMD8lgYVhScFh5e', 'X8baci2TMGEcE', 'dry8S89ncvPMrmgwvr']

    rand_num = random.randint(0, 7)

    if user_answer == get_trivia_api_latest_resp()[6]:
        result = ["correct_answer", giphy_correct[rand_num]]
        update_user_score(score=10, res="correct_answer")
    elif user_answer == "I don't know":
        result = ["not_know", giphy_notknow[rand_num]]
        update_user_score(score=0, res="not_know")
    else:
        result = ["incorrect_answer", giphy_incorrect[rand_num]]
        update_user_score(score=0, res="incorrect_answer")
    
    
    # Segment Track event API call to record the user action
    if current_user.is_authenticated:
        analytics.track(current_user.id, 'Open_Trivia', {'result':result[0]})
    else:
        analytics.track('12345', 'Open_Trivia', {'result':result[0]})
            
    return result
