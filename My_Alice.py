import json
import logging
from random import choice

from flask import Flask, request, jsonify

from Key_Phrase import *

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

Episode = 'Начало'


@app.route("/", methods=["POST"])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return jsonify(response)


def handle_dialog(response, request):
    global Episode
    if request["session"]["new"]:
        start(response)
    elif Episode == 'Выбор начать игру или нет':
        choose(response)
    else:
        end(response)


def start(response):
    global Episode
    response["response"]["text"] = choice(Greet_phrase)
    Episode = 'Выбор начать игру или нет'
    return

def choose(response):
    global Episode
    for agree in Agreement:
        if agree in request.json["request"]["command"]:
            response["response"]["text"] = f'{choice(Continue)} {choice(Choose)}'
            Episode = 'Выбор режима'
            return
    for disagree in Rejection:
        if disagree in request.json["request"]["command"]:
            return end(response)
    return choose_mistake(response, count=3)


def end(response):
    response["response"]["text"] = choice(Bye)
    return


def mistake(response):
    response["response"]["text"] = choice(Mistake)
    return


def choose_mistake(response, count):
    if count == 3:
        response["response"]["text"] = choice(IncorrectStep1)
        for agree in Agreement:
            if agree in request.json["request"]["command"]:
                response["response"]["text"] = f'{choice(Continue)} {choice(Choose)}'
            return
        for disagree in Rejection:
            if disagree in request.json["request"]["command"]:
                return end(response)
        return choose_mistake(response, count - 1)
    elif count == 2:
        response["response"]["text"] = choice(IncorrectStep2)
        for agree in Agreement:
            if agree in request.json["request"]["command"]:
                response["response"]["text"] = f'{choice(Continue)} {choice(Choose)}'
            return json.dumps(response)
        for disagree in Rejection:
            if disagree in request.json["request"]["command"]:
                return end(response)
        return choose_mistake(response, count - 1)
    else:
        response["response"]["text"] = IncorrectStep3


if __name__ == '__main__':
    app.run()
