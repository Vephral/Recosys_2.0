import requests
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
        messages = ['Бла', 'Бла', 'Бла', 'Бла']
        for message in messages:
            send_message(self.user_id, randint(0, 100000), message)

    # функция, которая активируется при ключевом слове "Инструкция по применению"
    def give_instructions(self):
        messages = ['Бла', 'Бла', 'Бла', 'Бла']
        for message in messages:
            send_message(self.user_id, randint(0, 100000), message)

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
                if similar is None:
                    message = 'В названии объекта присутствуют ошибки или данного объекта нет в нашей базе данных'
                    send_message(self.user_id, randint(0, 100000), message)
