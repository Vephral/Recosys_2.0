import requests


# логично, но функция, которая отправляет сообщение пользователю
def send_message(user_id, random_id, message):
    params = {'user_id': user_id, 'random_id': random_id, 'message': message}
    requests.request('GET',
                     'https://api.vk.com/method/messages.send?&access_token='
                     '...'
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


# функция, которая забирает ключ, ссылку на сервер и, судя по всему, уникальное значение для сообщения
def give_key_server_and_ts(group_id: str, access_token: str, ver: str):
    params = {'group_id': group_id}
    request = requests.request('GET',
                               'https://api.vk.com/method/groups.getLongPollServer?&access_token'
                               '=' + access_token + '&v=' + ver, params=params)
    # ответ всегда приходит в виде json
    response = request.json()
    return response['response']['key'], response['response']['server'], response['response']['ts']
