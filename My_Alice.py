import logging
import sqlite3
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
                Secret_Button, End_Button]

# Переменные для навыка
Picture_Id = ''
Question = ''
Answer = ''
Description = ''


@app.route("/", methods=["POST"])
# Главная функция, формирующая response
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


# Функция, которая решает, какая функция будет вызвана следующей
def handle_dialog(response, request):
    global Episode, count_choose_mem_word_mistake, count_choose_mistake
    if request["session"]["new"]:
        start(response)
    elif count_choose_mem_word_mistake != 3:
        choose_mem_word_mistake(response)
    elif count_choose_mistake != 3:
        choose_mistake(response)
    elif request["request"]["type"] == "SimpleUtterance":
        if Secret == request["request"]["command"]:
            secret_joke(response)
        elif 'хватит' == request["request"]["command"]:
            end(response)
        # elif Day_joke == request["request"]["command"]:
        #     daily_joke(response)
        elif Episode == 'Выбор начать игру или нет':
            choose(response)
        elif Episode == 'Варианты режима':
            for mem in Mem:
                if mem in request["request"]["command"]:
                    count_choose_mem_word_mistake = 3
                    new_mem(response)
            for word in Word:
                if word in request["request"]["command"]:
                    count_choose_mem_word_mistake = 3
                    new_word(response)
        elif Episode == 'Выбор режима':
            choose_mem_word(response)
        elif Episode == 'Новое слово':
            new_word(response)
        elif Episode == 'Слово ответ':
            if Answer in request["request"]["command"]:
                correct_word(response)
            else:
                incorrect_word(response)
        elif Episode == 'Мем ответ':
            if Answer in request["request"]["command"]:
                correct_mem(response)
            else:
                incorrect_mem(response)
        elif Episode == 'Слово, идем дальше?':
            for agree in Agreement:
                if agree in request["request"]["command"]:
                    new_word(response)
            for disagree in Rejection:
                if disagree in request["request"]["command"]:
                    end(response)
            else:
                mistake(response)
        elif Episode == 'Мем, идем дальше?':
            for agree in Agreement:
                if agree in request["request"]["command"]:
                    new_mem(response)
            for disagree in Rejection:
                if disagree in request["request"]["command"]:
                    end(response)
            else:
                mistake(response)
        elif Episode == 'Выход':
            end(response)
        else:
            mistake(response)
    elif request["request"]["type"] == "ButtonPressed":
        if Secret_Name_Button == request["request"]["payload"]["text"]:
            secret_joke(response)
        # elif Day_Joke_Name_Button == request["request"]["payload"]["text"]:
        #     daily_joke(response)
        elif End_Name_Button == request["request"]["payload"]["text"]:
            end(response)
        elif Support_Name_Button == request["request"]["payload"]["text"]:
            support(response)
        elif Ability_Name_Button == request["request"]["payload"]["text"]:
            ability(response)
        elif Agree_Name_Button == request["request"]["payload"]["text"]:
            if Episode == 'Выбор начать игру или нет':
                count_choose_mistake = 3
                mem_word(response)
            elif Episode == 'Слово, идем дальше?':
                new_word(response)
            elif Episode == 'Мем, идем дальше?':
                new_mem(response)
            else:
                mistake(response)
        elif Disagree_Name_Button == request["request"]["payload"]["text"]:
            count_choose_mistake = 3
            end(response)
        elif Another_Name_Button == request["request"]["payload"]["text"]:
            if 'Мем' in Episode or 'мем' in Episode:
                Episode = 'Новое слово'
                new_word(response)
            else:
                Episode = 'Новый мем'
                new_word(response)
        elif Episode == 'Выбор режима':
            if Mem_Name_Button == request["request"]["payload"]["text"]:
                count_choose_mem_word_mistake = 3
                new_mem(response)
            elif Word_Name_Button == request["request"]["payload"]["text"]:
                count_choose_mem_word_mistake = 3
                new_word(response)
        else:
            mistake(response)
    else:
        mistake(response)


# Функция, приветствующая пользователя и предоставляющая выбор о начале игры
def start(response):
    global Episode, Button_group
    Button_group = [Agree_Button, Disagree_Button,
                    Support_Button, Ability_Button,
                    Secret_Button, End_Button]
    response["response"]["text"] = Greet_phrase
    response["response"][
        "tts"] = f'<speaker audio="alice-sounds-game-powerup-2.opus"> Привет, чемпион! Хочешь поиграть в "Мемный сленг"? Нужно угадать по фотографии или описанию загаданное "мемное" слово. Если понадобится помощь, то просто скажи "Помощь",  а если захочешь узнать, что я умею, спроси "Что ты умеешь?". Погнали?'
    response["response"]["buttons"] = Button_group
    Episode = 'Выбор начать игру или нет'
    return


# Функция, обрабатывающая результат пользователя на первый вопрос о начале игры
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


# Функция окончания игры
def end(response):
    global Episode
    Episode = 'Начало'
    response["response"]["text"] = choice(Bye)
    response["response"][
        "tts"] = '<speaker audio="dialogs-upload/b0698619-d392-4049-831d-954551a74d66/62880414-c7e9-45bb-8d3c-aec37a204c24.opus"> До скорых встреч!'
    response["response"]["card"] = {'type': 'BigImage',
                                    'image_id': '997614/e54eab84a01b2c12008f',
                                    'description': choice(Bye)}
    response["response"]["end_session"] = True
    return


# Функция отработки ошибок
def mistake(response):
    response["response"]["text"] = choice(Mistake)
    return


# Функция помощи
def support(response):
    global Button_group
    response["response"]["text"] = Support
    response["response"]["buttons"] = Button_group
    return


# Функция ЧТО ТЫ УМЕЕШЬ?
def ability(response):
    global Button_group
    response["response"]["text"] = Ability
    response["response"]["buttons"] = Button_group
    return


# Функция, которая предлагает выбор режима игры
def mem_word(response):
    global Episode, Button_group
    response["response"]["text"] = choice(Choose)
    Button_group = [Mem_Button, Word_Button, Support_Button, Ability_Button,
                    Secret_Button, End_Button]
    response["response"]["buttons"] = Button_group
    Episode = 'Выбор режима'
    return


# Функция выбора режима игры
def choose_mem_word(response):
    global Episode, Button_group
    for mem in Mem:
        if mem in request.json["request"]["command"]:
            response["response"][
                "text"] = choice(Mem_phrase)
            Episode = 'Новый мем'
            Button_group = [Support_Button, Ability_Button,
                            Secret_Button, End_Button]
            response["response"]["buttons"] = Button_group
            return
    for word in Word:
        if word in request.json["request"]["command"]:
            response["response"][
                "text"] = choice(Word_phrase)
            Episode = 'Новое слово'
            Button_group = [Support_Button, Ability_Button,
                            Secret_Button, End_Button]
            response["response"]["buttons"] = Button_group
            return
    return choose_mem_word_mistake(response)


# Функция отправляющая рандомную шутку на английском языке
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


# Функция, отправляющая рандомную шутку на русском языке
# def daily_joke(response):
#     url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious," \
#           "political,racist,sexist,explicit"
#     res = requests.get(url)
#     json_response = res.json()
#     ru_joke = list()
#     ru_joke_correct = ''
#     if 'setup' in json_response:
#         setup = json_response['setup']
#         deliver = json_response['delivery']
#         ru_joke.append(setup)
#         ru_joke.append(deliver)
#     else:
#         joke = json_response['joke']
#         ru_joke.append(joke)
#     translator = Translator()
#     ru_joke_tr = translator.translate(ru_joke, src='en', dest='ru')
#     for i in range(len(ru_joke_tr)):
#         if i != 0:
#             ru_joke_correct += ' '
#         ru_joke_correct += ru_joke_tr[i].text
#     if ru_joke_correct != '':
#         response["response"]["text"] = ru_joke_correct
#         response["response"]["buttons"] = Button_group
#         return
#     else:
#         return mistake(response)


# Функция, обрабатывающая ошибки при первом выборе начала игры
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


# Функция, обрабатывающая ошибки при выборе режима игры
def choose_mem_word_mistake(response):
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


# Далее функции, содержащие в названии слово word
# Они обеспечивают работу режима слова
def new_word(response):
    global Question, Answer, Description, Episode
    con = sqlite3.connect("Alice_db.sqlite")
    cur = con.cursor()
    result = cur.execute(
        """SELECT * FROM `word` ORDER BY RANDOM() LIMIT 1""").fetchall()
    for data in result:
        Question = data[0]
        Answer = data[1]
        Description = data[2]
    con.close()
    response["response"]["text"] = Question
    Episode = 'Слово ответ'
    return


def correct_word(response):
    global Description, Button_group, Episode
    response["response"][
        "text"] = f'{choice(Praise)} А ты знал, что {Description} Погнали дальше?'
    Button_group = [Agree_Button, Disagree_Button, Another_Button,
                    Support_Button, Ability_Button,
                    Secret_Button, End_Button]
    response["response"]["buttons"] = Button_group
    Episode = 'Слово, идем дальше?'
    return


def incorrect_word(response):
    global Description, Button_group, Episode
    response["response"][
        "text"] = f'{choice(Condemnation)} Правильный ответ: {Answer}. А ты знал, что {Description} Погнали дальше?'
    Button_group = [Agree_Button, Disagree_Button, Another_Button,
                    Support_Button, Ability_Button,
                    Secret_Button, End_Button]
    response["response"]["buttons"] = Button_group
    Episode = 'Слово, идем дальше?'
    return


# Далее функции, содержащие в названии слово mem
# Они обеспечивают работу режима мем
def new_mem(response):
    global Question, Answer, Description, Episode, Picture_Id
    con = sqlite3.connect("Alice_db.sqlite")
    cur = con.cursor()
    result = cur.execute(
        """SELECT * FROM `mem` ORDER BY RANDOM() LIMIT 1""").fetchall()
    for data in result:
        Picture_Id = data[0]
        Question = data[1]
        Answer = data[2]
        Description = data[3]
    con.close()
    response["response"]["text"] = Question
    response["response"]["card"] = {'type': 'BigImage',
                                    'image_id': Picture_Id,
                                    'description': Question}
    Episode = 'Мем ответ'
    return


def correct_mem(response):
    global Description, Button_group, Episode
    response["response"][
        "text"] = f'{choice(Praise)} А ты знал, что {Description} Погнали дальше?'
    Button_group = [Agree_Button, Disagree_Button, Another_Button,
                    Support_Button, Ability_Button,
                    Secret_Button, End_Button]
    response["response"]["buttons"] = Button_group
    Episode = 'Мем, идем дальше?'
    return


def incorrect_mem(response):
    global Description, Button_group, Episode
    response["response"][
        "text"] = f'{choice(Condemnation)} Правильный ответ: {Answer}. А ты знал, что {Description} Погнали дальше?'
    Button_group = [Agree_Button, Disagree_Button, Another_Button,
                    Support_Button, Ability_Button,
                    Secret_Button, End_Button]
    response["response"]["buttons"] = Button_group
    Episode = 'Мем, идем дальше?'
    return


if __name__ == '__main__':
    app.run()
