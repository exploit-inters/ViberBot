# encoding=utf-8
from time import sleep
from flask import *
import json
import requests
# from flask_sslify import SSLify
from random import *
import re
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import datetime
import threading
import shutil
import os

app = Flask(__name__)
# sslify = SSLify(app)

TOKEN = ''
URL = 'https://chatapi.viber.com/pa/'
HEADER = {}
EVENTS = {}


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def getMemasik():
    url = choice(requests.get(
        'https://memeus.ru/api/v1/posts?page=' + str(randint(1, 50000)) + '&pageSize=5&type=fresh').json())['media'][0][
        'original']['path']
    # r = requests.get(url, stream=True)
    # with open('img', 'wb') as f:
    #     shutil.copyfileobj(r.raw, f)
    return url


def sendMessage(to, text='', type='text', header=HEADER):
    url = 'send_message'
    if type == 'text':
        answer = {'receiver': to, 'type': type, 'text': text}
    elif type == 'file':
        src = getMemasik()
        answer = {'receiver': to, 'type': type, 'media': src, 'size': os.path.getsize('img'),
                  'file_name': src.split('/')[-1]}
        print(answer)
    elif type == 'picture':
        src = getMemasik()
        answer = {'receiver': to, 'type': type, 'text': text, 'media': src, 'thumbnail': ''}
    return requests.post(URL + url, json=answer, headers=header).json()


def getComment(keyword):
    return requests.get('http://slogen.ru/ajax/slogan.php?type=2&word=' + keyword + '&_=1518616117262').text


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            r = request.get_json()
            if r['event'] == 'message':
                sender = r['sender']['id']
                type_message = r['message']['type']
                prevEvent = EVENTS.get(sender)
                EVENTS[sender] = type_message
                text_message = r['message']['text'] if type_message == 'text' else ''
                if prevEvent != 'picture' and type_message == 'text':
                    # Залогировали сообщение
                    if re.search(r'\?', text_message):
                        with open(r['sender']['name'] + ' ' + r['sender']['id'] + '_questions.txt', 'a') as f:
                            f.write(text_message + '\n')
                    else:
                        with open(r['sender']['name'] + ' ' + r['sender']['id'] + '.txt', 'a') as f:
                            f.write(
                                str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")) + ': ' + text_message + '\n')
                    # Парсим текст и отправляем ответ
                    parse_text(text_message, sender)
                elif prevEvent == 'picture' and type_message == 'text':
                    sendMessage(sender, text=getComment(text_message), header=HEADER)
                elif type_message == 'picture':
                    sendMessage(sender, text=choice(['Что тут?', 'Это чё?', 'Шо здесь?', 'Говори, что тут']),
                                header=HEADER)
                else:
                    sendMessage(sender, 'o_O Это что-то новенькое, я научусь этому позже', header=HEADER)
                    write_json(r, 'response' + str(r['timestamp']) + '.json')
            else:
                write_json(r, 'response' + str(r['event']) + '.json')
        except:
            pass

        return jsonify(r)
    if request.args.get('sendmessage'):
        sendMessage(request.args.get('sendmessage'), request.args.get('text'), header=HEADER)
    return '<h1>Hallo, my love <3</h1>'


def getLetter(flag):
    # Константы максимальных страниц
    lover_max = 17
    good_night = 19
    good_morning = 17
    miss_you = 15
    kompliment = 9

    # Формирование адреса к сайту с случайной страницей
    if flag == 'lover':
        st = randint(0, lover_max)
        url = str(st) + '.htm' if st > 0 else ''
        r = requests.get('http://lovefond.ru/stihi/priznanie/lyubimoy-devushke/' + url)
    elif flag == 'goodMorning':
        st = randint(0, good_morning)
        url = str(st) + '.htm' if st > 0 else ''
        r = requests.get('http://lovefond.ru/stihi/dobroe-utro/lyubimaya/' + url)
    elif flag == 'goodNight':
        st = randint(0, good_night)
        url = str(st) + '.htm' if st > 0 else ''
        r = requests.get('http://lovefond.ru/stihi/spokoynoy-nochi/lyubimoy-devushke/' + url)
    elif flag == 'miss':
        st = randint(0, miss_you)
        url = str(st) + '.htm' if st > 0 else ''
        r = requests.get('http://lovefond.ru/stihi/skuchayu/lyubimoy-devushke/' + url)
    elif flag == 'kompliment':
        st = randint(0, kompliment)
        url = str(st) + '.htm' if st > 0 else ''
        r = requests.get('http://lovefond.ru/stihi/komplimenty/devushke/' + url)

    # Парсинг страницы, выбор случайного стиха
    http_encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(r.content, is_html=True)
    encoding = html_encoding or http_encoding
    soup = BeautifulSoup(r.content, 'html.parser', from_encoding=encoding)
    letter = choice(soup.find_all('p', class_='sfst')).getText('\n')

    return letter


def getAnswer(question):
    res = False
    answer = ['Не понял вопроса', 'Я добавил вопрос в базу данных, потом разберусь',
              'Ответ на этот вопрос мне не известен', 'Я не знаю', 'Лучше спросить это у Google']
    with open('questions.txt', 'r') as f:
        for line in f:
            if res:
                answer = line.split('/')
                break
            if question in line:
                res = True
    return choice(answer)


def parse_text(text_message, to):
    answers = []
    love_smiles = ['(mwah)', '(heart)', '(fire)', '(purple_heart)', '(moa)', '(inlove)']
    if re.match(r'П?п?ривет', text_message):
        with open('hello.txt', 'r') as f:
            for line in f:
                answers.append(line)
        sendMessage(to, choice(answers), header=HEADER)
    elif re.match(r'Ф?ф?акт', text_message):
        with open('fakts.txt', 'r') as f:
            for line in f:
                answers.append(line)
        sendMessage(to, choice(answers), header=HEADER)
    elif text_message in love_smiles:
        sendMessage(to, choice(love_smiles))
    elif re.search(r'Л?л?юблю тебя\w*', text_message) or re.search(r'Т?т?ебя Л?л?юблю\w*', text_message) or re.search(
            r'очень люблю', text_message):
        sendMessage(to, getLetter('lover'), header=HEADER)
    elif re.match(r'м?М?емасик', text_message):
        sendMessage(to, '', 'picture', header=HEADER)  # Отправка картинки
    elif re.match(r'С?с?покойной ноч\w*', text_message) or re.match(r'С?с?лад\w*.[^ ]*\sснов', text_message):
        sendMessage(to, getLetter('goodNight'), header=HEADER)
    elif re.match(r'Д?д?обро.*[^ ]\sутр', text_message):
        sendMessage(to, getLetter('goodMorning'), header=HEADER)
    elif re.match(r'я?Я? скучаю', text_message) or re.search(r'с?С?кучаю по тебе', text_message) or re.search(
            r'с?С?оскучилась', text_message) or re.search(r'с?С?кучаю', text_message):
        sendMessage(to, getLetter('miss'), header=HEADER)
    elif re.search(r'к?К?омплимент', text_message):
        sendMessage(to, getLetter('kompliment'), header=HEADER)
    elif re.search(r'\?', text_message):
        sendMessage(to, text=getAnswer(text_message.lower()), header=HEADER)
    else:
        with open('answers.txt', 'r') as f:
            for line in f:
                answers.append(line)
        sendMessage(to, choice(answers), header=HEADER)


def run():
    app.run()


def setWebHook(url, delete=False):
    if delete:
        data = {'url': ''}
    else:
        data = {'url': url.strip(' '),
                'event_types': ['delivered', 'seen', 'failed', 'subscribed', 'unsubscribed', 'conversation_started']}
    r = requests.post('https://chatapi.viber.com/pa/set_webhook', json=data, headers=HEADER)
    if r.json()['status'] == 0:
        print('Web hook успешно установлен!')
    else:
        print('Произошла какая-то ошибка')


if __name__ == '__main__':
    TOKEN = input('Введите токен: ')
    HEADER = {'X-Viber-Auth-Token': TOKEN}
    print('[+]: 1 для запуска бота\n')
    print('[+]: 2 для установки web hook\'\n')
    print('[+]: 3 для удаления web hook\'\n')
    code = input('')

    if code == '1':
        app.run()
    elif code == '2':
        ur = input('Введите ссылку web hook\'a: ')
        thr1 = threading.Thread(target=run)
        thr2 = threading.Thread(target=setWebHook, args=(ur, False))
        thr1.start()
        sleep(1)
        thr2.start()
    elif code == '3':
        setWebHook('', True)
