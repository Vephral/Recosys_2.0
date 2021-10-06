import time
import asyncio
import aiohttp
import requests
import pandas as pd

url = 'https://id.twitch.tv/oauth2/token?client_id=...&client_secret=...&grant_type=client_credentials'
response = requests.request('POST', url=url)
access_token = response.text
client_id = '...'
print(access_token)

text_cols = ['storyline', 'summary']
cols = ['id', 'name', 'age_ratings', 'slug', 'aggregated_rating', 'aggregated_rating_count', 'category', 'collection',
        'alternative_names', 'external_games', 'first_release_date', 'game_engines', 'game_modes', 'genres',
        'involved_companies', 'keywords', 'platforms', 'rating', 'player_perspectives', 'dlcs', 'franchise',
        'rating_count', 'release_dates', 'similar_games', 'tags', 'parent_game', 'status',
        'total_rating', 'total_rating_count', 'updated_at', 'websites']


async def create_games_dataset(floor, ceiling, endpoint='games'):
    # нужно для того, чтобы авторизироваться
    headers = {'Client-ID': client_id,
               'Authorization': access_token}
    async with aiohttp.ClientSession() as session:
        all_games = pd.DataFrame(columns=cols)
        for i in range(floor, ceiling):
            # endpoint и id можно изменять для того, чтобы получить разные наборы
            body = 'fields *; where id = ' + str(i) + ';'
            async with session.post('https://api.igdb.com/v4/' + endpoint + '/', headers=headers, data=body) as resp:
                game = await resp.json()
                try:  # если вышла такая ошибка, значит слишком много запросов в одну секунду
                    # на тот случай, если id нет в базе данных
                    if len(game) > 0:
                        all_games.loc[len(all_games.index)] = game[0]
                except KeyError:  # поэтому, ждем 1 секунду и делаем новый запрос
                    time.sleep(3)
                    async with session.post('https://api.igdb.com/v4/' + endpoint + '/', headers=headers, data=body) as resp:
                        game = await resp.json()
                        if len(game) > 0:
                            all_games.loc[len(all_games.index)] = game[0]
        return all_games


start_time = time.time()
games_dataset = asyncio.run(create_games_dataset(1, 10))
print("--- %s seconds ---" % (time.time() - start_time))
print(games_dataset.head())
