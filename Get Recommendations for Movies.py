import requests
import numpy as np
import pandas as pd
import tmdbsimple as tmdb

tmdb.API_KEY = '...'

movies_dataset = pd.read_csv('./datasets/movies_dataset/movies_clear.csv')
ids = movies_dataset.id


def get_recommendations(item_id):
    try:  # если есть рекомендации, то выполняем код
        movie = tmdb.Movies(item_id)
        recs = movie.recommendations()['results'][:7]
    except requests.HTTPError:  # если их нет, то возвращаем пропущенные значения
        recs = [{'title': np.NaN, 'id': np.NaN}, {'title': np.NaN, 'id': np.NaN}]
    return recs


movie_recs = pd.DataFrame(columns=['ID', 'Reco_Title', 'Reco_ID'])

for item_id in ids:
    # в том случае, если что-то пошло не так и алгоритм закончил исполнение,
    # те значения, что уже были пропарсены, остаются в df
    if item_id in movie_recs.ID.unique():
        continue
    # те значения, что не были пропарсены, парсятся дальше
    if item_id not in movie_recs.ID.unique():
        sims = get_recommendations(item_id)
        for sim in sims:
            movie_recs.loc[len(movie_recs.index)] = [item_id, sim['title'], sim['id']]
        if len(movie_recs) % 100 == 0:
            print(len(movie_recs))

movie_recs.to_csv('./datasets/movies_dataset/recommendations.csv')
print(movie_recs.head())
