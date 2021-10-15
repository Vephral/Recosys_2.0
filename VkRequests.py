import requests

# логично, но функция, которая отправляет сообщение пользователю
def send_message(user_id, random_id, message):
    params = {'user_id': user_id, 'random_id': random_id, 'message': message}
    requests.request('GET',
                     'https://api.vk.com/method/messages.send?&access_token='
                     '3b156916467056f5d6dc91341ea329ae212a49674024fa603aa93c77e435fefaf6a697a151fad4220f266'
                     '&v=5.122',
                     params=params)


# функция, которая создает запрос к серверу и ожидает новых событий
def create_longpoll(server, key, ts):
    longpoll_listen = requests.request('POST', server + '?act=a_check&key=' + key + f'&ts={ts}&wait=25')
    events = longpoll_listen.json()
    if 'failed' in events.keys():
        print('Reactivate Function')
        return None
    return events

