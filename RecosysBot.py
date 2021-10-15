import requests
from time import sleep
from random import randint
import GiveRecommendations as gr


# логично, но функция, которая отправляет сообщение пользователю
def send_message(user_id, random_id, message):
    params = {'user_id': user_id, 'random_id': random_id, 'message': message}
    requests.request('GET',
                     'https://api.vk.com/method/messages.send?&access_token='
                     '3b156916467056f5d6dc91341ea329ae212a49674024fa603aa93c77e435fefaf6a697a151fad4220f266'
                     '&v=5.122',
                     params=params)


class RecosysBot:
    def __init__(self, user_message, user_id):
        self.user_message = user_message
        self.user_id = user_id

    # функция, которая активируется при ключевом слове "Запуск"
    def recosys_start(self):
        messages = ['Приветствую! Я чат-бот Рекосис.',
                    'Все, что я могу - рекомендовать тебе что-нибудь, на основе выбранного тобой объекта.',
                    'Объект - название аниме, фильма или игры. (да, список скудный, но что есть, то есть)',
                    'Чтобы начать пользоваться, рекомендую ознакомиться с инструкцией по применению.',
                    'Список доступных команд: "Инструкция по применению", "Запуск", "Дать рекомендацию"']
        for message in messages:
            send_message(self.user_id, randint(0, 100000), message)
            sleep(5)

    # функция, которая активируется при ключевом слове "Инструкция по применению"
    def give_instructions(self):
        messages = ['Итак, вы воспользовались командой "Инструкция по применению".',
                    'Чтобы получить рекомендацию, нужно:',
                    'Во-первых, написать команду "Дать рекомендацию".',
                    'Во-вторых, написать тип рекомендации. Тип рекомендации - тип объекта. Например, аниме.',
                    'В-третьих, написать название того объекта, рекомендации на основе которого будут вычисляться.',
                    'И... Все. Дальше нужно какое-то время подождать своих рекомендаций. Где-то дольше, где-то короче.']
        for message in messages:
            send_message(self.user_id, randint(0, 100000), message)
            sleep(5)

    # функция, которая выводит некоторые пояснения по рекомендациям и наборам данных
    def give_refinements(self):
        messages = ['Так, по поводу объектов есть некоторые уточнения.',
                    'Данные взяты с этих сайтов, так что, если хотите, чтобы алгоритм нашел ваш объект, сверяйтесь:',
                    '- IGDB (Internet Game Database) - сайт с данными по играм.',
                    '- TMDB (The Movie Database) - сайт с данными по фильмам.',
                    '- MAL (My Anime List) - сайт с данными по аниме.',
                    'Также, вполне возможно, что даже если название было введено правильно, алгоритм может не найти ваш объект.',
                    'Это может произойти по разным причинам для разных наборов данных: ',
                    'Если для фильмов, то тот набор уже сильно устарел, поэтому не рекомендую кидать объекты, которые вышли позже 2017 года.',
                    'Если для игр (в чем я очень сомневаюсь, так как набор был сделан мной, буквально пару недель назад), то проверяйте название.'
                    'С моей стороны нет никаких ошибок. Все вышедшие, на данный момент, игры присутствуют в наборе.',
                    'Если для аниме (в чем я также сомневаюсь, так как набор свежий), то, вполне возможно, что вы выбрали'
                    'самые новейшие тайтлы, которых попросту нет в базе данных.',
                    'Теперь, - самое важное уточнение - рекомендации работают плохо, поэтому пользуйтесь на свой страх и риск.',
                    'У меня все. Удачи.']
        for message in messages:
            send_message(self.user_id, randint(0, 100000), message)
            sleep(5)

    def take_recommendations(self, ts):
        # новое ожидание ответа от пользователя для того, чтобы получить название объекта
        new_longpoll_listen = requests.request('POST',
                                               'https://lp.vk.com/wh197988828?act=a_check&key'
                                               '=fc005e05c8823444da7c9e0ea6c25b124aa8cff7&ts={0}&wait=25'.format(ts))
        new_events = new_longpoll_listen.json()
        for event in new_events['updates']:
            if event['type'] == 'message_new':
                user_item = event['object']['message']['text']
                similar = gr.give_recommendations(user_item, self.user_message)
                # в том случае, если названия объекта нет в базе данных, функция вернет None
                if similar is not None:
                    for rank in range(7):
                        message = str(rank + 1) + ' - ' + similar[rank]
                        send_message(self.user_id, randint(0, 100000), message)
                        sleep(2)
                if similar is None:
                    message = 'В названии объекта присутствуют ошибки или данного объекта нет в нашей базе данных'
                    send_message(self.user_id, randint(0, 100000), message)
