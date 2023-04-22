import logging
from random import choice

from flask import Flask, request, jsonify

from Bot_Key_Phrase import *
from User_Key_Phrase import *

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

Episode = 'Начало'
count_choose_mistake = 3


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
    elif count_choose_mistake != 3:
        choose_mistake(response)
    elif Episode == 'Выбор начать игру или нет':
        choose(response)
    elif Episode == 'Варианты режима':
        mem_word(response)
    elif Episode == 'Выход':
        end(response)
    else:
        pass


def start(response):
    global Episode
    response["response"]["text"] = choice(Greet_phrase)
    Episode = 'Выбор начать игру или нет'
    return


def choose(response):
    global Episode
    for agree in Agreement:
        if agree in request.json["request"]["command"]:
            response["response"][
                "text"] = f'{choice(Continue)} {choice(Choose)}'
            Episode = 'Варианты режима'
            return
    for disagree in Rejection:
        if disagree in request.json["request"]["command"]:
            return end(response)
    return choose_mistake(response)


def end(response):
    response["response"]["text"] = choice(Bye)
    return


def mistake(response):
    response["response"]["text"] = choice(Mistake)
    return


def mem_word(response):
    global Episode
    response["response"]["text"] = choice(Choose)
    Episode = 'Выбор режима'
    return


def choose_mem_word(response):
    global Episode
    for mem in Mem:
        if mem in request.json["request"]["command"]:
            response["response"][
                "text"] = f'{choice(Continue)} {choice(Choose)}'
            Episode = 'Новый мем'
            return
    for word in Word:
        if word in request.json["request"]["command"]:
            response["response"][
                "text"] = f'{choice(Continue)} {choice(Choose)}'
            Episode = 'Новое слово'
    for sound in Sound:
        if sound in request.json["request"]["command"]:
            response["response"][
                "text"] = f'{choice(Continue)} {choice(Choose)}'
            Episode = 'Новый звук'
    return choose_mem_word_mistake(response)


def choose_mistake(response):
    global count_choose_mistake, Episode
    if count_choose_mistake == 3:
        count_choose_mistake -= 1
        response["response"]["text"] = choice(IncorrectStep1)
        return
    elif count_choose_mistake == 2:
        count_choose_mistake -= 1
        response["response"]["text"] = choice(IncorrectStep2)
        return
    else:
        count_choose_mistake = 3
        response["response"]["text"] = IncorrectStep3
        response["response"]["end_session"] = True
        Episode = 'Выход'
        return


def choose_mem_word_mistake(response):
    global count_choose_mistake
    global Episode
    if count_choose_mistake == 3:
        response["response"]["text"] = choice(IncorrectStep1)
        for mem in Mem:
            if mem in request.json["request"]["command"]:
                response["response"][
                    "text"] = f'{choice(Continue)} {choice(Choose)}'
                Episode = 'Новый мем'
                return
        for word in Word:
            if word in request.json["request"]["command"]:
                response["response"][
                    "text"] = f'{choice(Continue)} {choice(Choose)}'
                Episode = 'Новое слово'
        for sound in Sound:
            if sound in request.json["request"]["command"]:
                response["response"][
                    "text"] = f'{choice(Continue)} {choice(Choose)}'
                Episode = 'Новый звук'
        count_choose_mistake -= 1
        return choose_mistake(response)
    elif count_choose_mistake == 2:
        for mem in Mem:
            if mem in request.json["request"]["command"]:
                response["response"][
                    "text"] = f'{choice(Continue)} {choice(Choose)}'
                Episode = 'Новый мем'
                return
        for word in Word:
            if word in request.json["request"]["command"]:
                response["response"][
                    "text"] = f'{choice(Continue)} {choice(Choose)}'
                Episode = 'Новое слово'
        for sound in Sound:
            if sound in request.json["request"]["command"]:
                response["response"][
                    "text"] = f'{choice(Continue)} {choice(Choose)}'
                Episode = 'Новый звук'
        count_choose_mistake -= 1
        return choose_mistake(response)
    else:
        response["response"]["text"] = IncorrectStep3
        Episode = 'Выход'
        return


if __name__ == '__main__':
    app.run()
