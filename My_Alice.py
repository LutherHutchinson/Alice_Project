import logging
from random import choice

import requests
from flask import Flask, request, jsonify
from googletrans import Translator

from All_Buttons import *
from Bot_Key_Phrase import *
from User_Key_Phrase import *

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Флаг, который говорит о том, на каком этапе находится навык
Episode = 'Начало'

# Счетчик ошибок в начале игры
count_choose_mistake = 3

# Счетчик ошибок при выборе режима игры
count_choose_mem_word_mistake = 3

# Классический набор кнопок
Button_group = [Agree_Button, Disagree_Button,
                Support_Button, Ability_Button,
                Day_Joke_Button, Secret_Button,
                End_Button]


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
    elif count_choose_mem_word_mistake != 3:
        choose_mem_word_sound_mistake(response)
    elif count_choose_mistake != 3:
        choose_mistake(response)
    elif request["request"]["type"] == "SimpleUtterance":
        if Secret == request["request"]["command"]:
            secret_joke(response)
        elif Day_joke == request["request"]["command"]:
            daily_joke(response)
        else:
            mistake(response)
    elif request["request"]["type"] == "ButtonPressed":
        if Secret_Name_Button == request["request"]["payload"]["text"]:
            secret_joke(response)
        elif Day_Joke_Name_Button == request["request"]["payload"]["text"]:
            daily_joke(response)
        else:
            mistake(response)
    elif Episode == 'Выбор начать игру или нет':
        choose(response)
    elif Episode == 'Варианты режима':
        mem_word_sound(response)
    elif Episode == 'Выбор режима':
        choose_mem_word_sound(response)
    elif Episode == 'Выход':
        end(response)
    else:
        mistake(response)


def start(response):
    global Episode, Button_group
    response["response"]["text"] = choice(Greet_phrase)
    response["response"]["buttons"] = Button_group
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
    global Episode
    Episode = 'Начало'
    response["response"]["text"] = choice(Bye)
    return


def mistake(response):
    response["response"]["text"] = choice(Mistake)
    return


def mem_word_sound(response):
    global Episode, Button_group
    response["response"]["text"] = choice(Choose)
    Button_group = [Mem_Button, Word_Button, Support_Button, Ability_Button,
                    Day_Joke_Button, Secret_Button, End_Button]
    response["response"]["buttons"] = Button_group
    Episode = 'Выбор режима'
    return


def choose_mem_word_sound(response):
    global Episode, Button_group
    for mem in Mem:
        if mem in request.json["request"]["command"]:
            response["response"][
                "text"] = choice(Mem_phrase)
            Episode = 'Новый мем'
            Button_group = [Support_Button, Ability_Button,
                            Day_Joke_Button, Secret_Button, End_Button]
            response["response"]["buttons"] = Button_group
            return
    for word in Word:
        if word in request.json["request"]["command"]:
            response["response"][
                "text"] = choice(Word_phrase)
            Episode = 'Новое слово'
            Button_group = [Support_Button, Ability_Button,
                            Day_Joke_Button, Secret_Button, End_Button]
            response["response"]["buttons"] = Button_group
            return
    return choose_mem_word_sound_mistake(response)


def choose_mistake(response):
    global count_choose_mistake, Episode
    if count_choose_mistake == 3:
        count_choose_mistake -= 1
        response["response"]["text"] = choice(IncorrectStep1_1)
        response["response"]["buttons"] = Button_group
        return
    elif count_choose_mistake == 2:
        count_choose_mistake -= 1
        response["response"]["text"] = choice(IncorrectStep2_1)
        response["response"]["buttons"] = Button_group
        return
    else:
        count_choose_mistake = 3
        response["response"]["text"] = IncorrectStep3_1
        response["response"]["end_session"] = True
        Episode = 'Начало'
        return


def choose_mem_word_sound_mistake(response):
    global count_choose_mem_word_mistake
    global Episode
    if count_choose_mem_word_mistake == 3:
        count_choose_mem_word_mistake -= 1
        response["response"]["text"] = choice(IncorrectStep1_2)
        response["response"]["buttons"] = Button_group
        return
    elif count_choose_mem_word_mistake == 2:
        count_choose_mem_word_mistake -= 1
        response["response"]["text"] = choice(IncorrectStep2_2)
        response["response"]["buttons"] = Button_group
        return
    else:
        count_choose_mem_word_mistake = 3
        response["response"]["text"] = IncorrectStep3_2
        response["response"]["end_session"] = True
        Episode = 'Начало'
        return


def secret_joke(response):
    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious," \
          "political,racist,sexist,explicit"
    res = requests.get(url)
    json_response = res.json()
    ru_joke = ''
    if 'setup' in json_response:
        setup = json_response['setup']
        deliver = json_response['delivery']
        ru_joke += setup
        ru_joke += deliver
    else:
        joke = json_response['joke']
        ru_joke += joke
    response["response"]["text"] = ru_joke
    if ru_joke != '':
        response["response"]["text"] = ru_joke
        response["response"]["buttons"] = Button_group
        return
    else:
        return mistake(response)


def daily_joke(response):
    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious," \
          "political,racist,sexist,explicit"
    res = requests.get(url)
    json_response = res.json()
    ru_joke = list()
    ru_joke_correct = ''
    if 'setup' in json_response:
        setup = json_response['setup']
        deliver = json_response['delivery']
        ru_joke.append(setup)
        ru_joke.append(deliver)
    else:
        joke = json_response['joke']
        ru_joke.append(joke)
    translator = Translator()
    ru_joke_tr = translator.translate(ru_joke, src='en', dest='ru')
    for i in range(len(ru_joke_tr)):
        if i != 0:
            ru_joke_correct += ' '
        ru_joke_correct += ru_joke_tr[i].text
    if ru_joke_correct != '':
        response["response"]["text"] = ru_joke_correct
        response["response"]["buttons"] = Button_group
        return
    else:
        return mistake(response)


if __name__ == '__main__':
    app.run()
