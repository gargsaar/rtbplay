from app import db
import requests
from flask_login import current_user
from sqlalchemy import text
import random
from flask import current_app
import html

opentdb_api_url = 'https://opentdb.com/api.php?amount=1&token='
trivia_response = {}
answer_choices = []


def trivia():
    global trivia_response
    token = current_app.config['TRIVIA_SESSION_TOKEN']
    response = requests.get(f"{opentdb_api_url}{token}").json()
    trivia_response.update(response)
    trivia_response["results"][0]["question"] = html.unescape(trivia_response["results"][0]["question"])
    return trivia_response


def answer_choices():
    ans_choices = []
    trivia_resp = trivia_response
    if trivia_resp["results"][0]["type"] == 'multiple':
        ans_choices = [html.unescape(trivia_resp["results"][0]["correct_answer"]),
                       html.unescape(trivia_resp["results"][0]["incorrect_answers"][0]),
                       html.unescape(trivia_resp["results"][0]["incorrect_answers"][1]),
                       html.unescape(trivia_resp["results"][0]["incorrect_answers"][2])
                       ]
        random.shuffle(ans_choices)
        ans_choices.append("I don't know")
    return ans_choices


def get_trivia_response():
    return trivia_response
