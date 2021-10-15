import requests
from time import sleep
import VkRequests as vr
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
        # мы должны захватить сразу два события, так как первое - состояние печатания, а второе - новое сообщение
        # по-другому просто не работает. не знаю почему.
        ts = str((int(ts)-2)+1)
        events = vr.create_longpoll(server, key, ts)
        print(events)
        # иногда, когда действие ключа истекает, выбрасывается ошибка
        for event in events['updates']:
            # другие события нам пока что не интересны
            if event['type'] == 'message_new':
                # если поставить тот же ts, то получится, что мы возьмем то же сообщение
                new_ts = str(int(events['ts']) + 1)
                user_id = event['object']['message']['from_id']
                user_message = event['object']['message']['text']
                # нужно, чтобы обдурить пользователей. ХАХАХАХХАХА.
                if user_message == 'Дать рекомендацию':
                    return None
                # ждем 25 секунд, так как рекомендованное значение ожидания (вверху) в longpoll - 25 секунд
                sleep(25)

                if user_message == 'Запуск':
                    rb.RecosysBot(user_message, user_id, server, key).recosys_start()
                if user_message == 'игры':
                    user_message = 'games'
                    rb.RecosysBot(user_message, user_id, server, key).take_recommendations(new_ts)
                if user_message == 'фильмы':
                    user_message = 'movies'
                    rb.RecosysBot(user_message, user_id, server, key).take_recommendations(new_ts)
                if user_message == 'аниме':
                    user_message = 'anime'
                    rb.RecosysBot(user_message, user_id, server, key).take_recommendations(new_ts)
                if user_message == 'Инструкция по применению':
                    rb.RecosysBot(user_message, user_id, server, key).give_instructions()
                    rb.RecosysBot(user_message, user_id, server, key).give_refinements()


if __name__ == '__main__':
    print(print_recommendations('vk'))
