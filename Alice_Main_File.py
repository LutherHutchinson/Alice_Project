import json
import logging
from random import randrange

from flask import Flask, request

from Key_Phrase import *

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logging.info(request.json)


@app.route("/", methods=["POST"])
def main():
    response = {
        "version": request.json["version"],
        "session": request.json["session"],
        "response": {
            "end_session": False
        }
    }

    req = request.json
    start(response, req)


def start(response, req):
    response["response"]["text"] = Greet_phrase[
        randrange(0, len(Greet_phrase))]
    send(response, req)


def send(response, req):
    print(response)
    return json.dumps(response)


if __name__ == '__main__':
    app.run()
