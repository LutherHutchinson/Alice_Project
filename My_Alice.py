import json
import logging
from random import randrange

from flask import Flask, request

from Key_Phrase import *

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


@app.route("/", methods=["POST"])
def main():
    logging.info(request.json)

    response = {
        "version": request.json["version"],
        "session": request.json["session"],
        "response": {
            "end_session": False
        }
    }

    if request.json["session"]["new"] == True:
        return start(response)
    else:
        return end(response)


def start(response):
    response["response"]["text"] = Greet_phrase[
        randrange(0, len(Greet_phrase))]
    return json.dumps(response), choose(response)


def choose(response):
    for agree in Agreement:
        if agree in request.json["request"]["command"]:
            response["response"]["text"] = f'{Continue} {Choose}'
            return json.dumps(response)
    for disagree in Rejection:
        if disagree in request.json["request"]["command"]:
            return end(response)
    return choose_mistake(response, count=3)


def end(response):
    response["response"]["text"] = Bye[randrange(0, len(Bye))]
    return json.dumps(response)


def mistake(response):
    response["response"]["text"] = Mistake[randrange(0, len(Mistake))]
    return json.dumps(response)


def choose_mistake(response, count):
    if count == 3:
        response["response"]["text"] = IncorrectStep1[
            randrange(0, len(IncorrectStep1))]
        for agree in Agreement:
            if agree in request.json["request"]["command"]:
                response["response"]["text"] = f'{Continue} {Choose}'
            return json.dumps(response)
        for disagree in Rejection:
            if disagree in request.json["request"]["command"]:
                return end(response)
        return choose_mistake(response, count - 1)
    elif count == 2:
        response["response"]["text"] = IncorrectStep2[
            randrange(0, len(IncorrectStep2))]
        for agree in Agreement:
            if agree in request.json["request"]["command"]:
                response["response"]["text"] = f'{Continue} {Choose}'
            return json.dumps(response)
        for disagree in Rejection:
            if disagree in request.json["request"]["command"]:
                return end(response)
        return choose_mistake(response, count - 1)
    else:
        response["response"]["text"] = IncorrectStep3
        return json.dumps(response)


if __name__ == '__main__':
    app.run()
