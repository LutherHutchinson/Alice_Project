import json
import logging
from random import randrange

from flask import Flask, request

from Key_Phrase import *

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)



@app.route("/", methods=["POST"])
class My_Alice:
    def __init__(self):
        logging.info(request.json)
        self.response = {
            "version": request.json["version"],
            "session": request.json["session"],
            "response": {
                "end_session": False
            }
        }

        if request.json["session"]["new"] == True:
            self.start()
        else:
            self.end()

    def start(self):
        self.response["response"]["text"] = Greet_phrase[
            randrange(0, len(Greet_phrase))]
        return json.dumps(self.response), self.choose()

    def choose(self):
        for agree in Agreement:
            if agree in request.json["request"]["command"]:
                self.response["response"]["text"] = f'{Continue} {Choose}'
            return json.dumps(self.response)

        for disagree in Rejection:
            if disagree in request.json["request"]["command"]:
                return self.end()
        return self.choose_mistake(count=3)

    def end(self):
        self.response["response"]["text"] = Bye[randrange(0, len(Bye))]
        return json.dumps(self.response)

    def mistake(self):
        self.response["response"]["text"] = Mistake[randrange(0, len(Mistake))]
        return json.dumps(self.response)

    def choose_mistake(self, count):
        if count == 3:
            self.response["response"]["text"] = IncorrectStep1[
                randrange(0, len(IncorrectStep1))]
            for agree in Agreement:
                if agree in request.json["request"]["command"]:
                    self.response["response"]["text"] = f'{Continue} {Choose}'
                return json.dumps(self.response)
            for disagree in Rejection:
                if disagree in request.json["request"]["command"]:
                    return self.end()
            return self.choose_mistake(count - 1)
        elif count == 2:
            self.response["response"]["text"] = IncorrectStep2[
                randrange(0, len(IncorrectStep2))]
            for agree in Agreement:
                if agree in request.json["request"]["command"]:
                    self.response["response"]["text"] = f'{Continue} {Choose}'
                return json.dumps(self.response)
            for disagree in Rejection:
                if disagree in request.json["request"]["command"]:
                    return self.end()
            return self.choose_mistake(count - 1)
        else:
            self.response["response"]["text"] = IncorrectStep3
            return json.dumps(self.response)


if __name__ == '__main__':
    app.run()
