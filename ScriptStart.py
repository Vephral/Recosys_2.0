import requests
from time import sleep
import RecosysBot as rb
import GiveRecommendations as gr


# функция, которая забирает ключ, ссылку на сервер и, судя по всему, уникальное значение для сообщения
def give_key_server_and_ts(group_id: str, access_token: str, ver: str):
    params = {'group_id': group_id}
    request = requests.request('GET',
                               'https://api.vk.com/method/groups.getLongPollServer?&access_token'
                               '=' + access_token + '&v=' + ver, params=params)
    # ответ всегда приходит в виде json
    response = request.json()
    return response['response']['key'], response['response']['server'], response['response']['ts']


# функция, которая в зависимости от параметра, выдает рекомендации на основе объекта
def print_recommendations(print_in='log'):
    # сделано так по двум причинам: во-первых, когда ключ придется изменить, все, что нужно - запустить ту же функцию
    # во-вторых, это безопаснее, так как все ключи нужно будет убрать, а тут их видно хорошо
    key, server, ts = give_key_server_and_ts(group_id='197988828',
                                             access_token='3b156916467056f5d6dc91341ea329ae212a49674024fa603aa93c77e435fefaf6a697a151fad4220f266',
                                             ver='5.122')
    if print_in == 'log':
        print('Write type of data: ')
        type_of_recs = input()
        print('Write item for recommendations: ')
        item = input()

        similar = gr.give_recommendations(item, type_of_recs)
        [print(i + 1, ' - ', similar[i]) for i in range(len(similar))]
    if print_in == 'vk':
        longpoll_listen = requests.request('POST', server + '?act=a_check&key=' + key + f'&ts={ts}&wait=25')
        events = longpoll_listen.json()
        # иногда, когда действие ключа истекает, выбрасывается ошибка
        if 'error' in events.keys():
            print('Reactivate Function')
            return None
        for event in events['updates']:
            # другие события нам пока что не интересны
            if event['type'] == 'message_new':
                # если поставить тот же ts, то получится, что мы возьмем то же сообщение
                new_ts = str(int(events['ts']) + 1)
                user_id = event['object']['message']['from_id']
                user_message = event['object']['message']['text']
                # ждем 25 секунд, так как рекомендованное значение ожидания (вверху) в longpoll - 25 секунд
                sleep(25)

                if user_message == 'Запуск':
                    rb.RecosysBot(user_message, user_id).recosys_start()
                if user_message in ['games', 'movies', 'anime']:
                    rb.RecosysBot(user_message, user_id).take_recommendations(new_ts)
                if user_message == 'Инструкция по применению':
                    rb.RecosysBot(user_message, user_id).give_instructions()


if __name__ == '__main__':
    print_recommendations('vk')
