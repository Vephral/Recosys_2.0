import pandas as pd
import jikanpy as jp
from time import sleep, time

jikan = jp.Jikan()
anime_dataset = pd.read_csv('./datasets/anime_dataset/anime.csv')
ids = anime_dataset.MAL_ID.tolist()


def get_cleared_recs(uncleared_recs):
    titles = []
    mal_ids = []
    index = 0
    while index != 7:
        try:
            title = uncleared_recs['recommendations'][i]['title']
            mal_id = uncleared_recs['recommendations'][i]['mal_id']
            titles.append(title)
            mal_ids.append(mal_id)
            index += 1
        except IndexError:
            titles.append('No')
            mal_ids.append('No')
            index += 1
    return titles, mal_ids


def get_recs(ID):
    uncleared_recs = jikan.anime(ID, extension='recommendations')
    recs = get_cleared_recs(uncleared_recs)
    return recs


anime_recs = pd.DataFrame(columns=['ID', 'Reco_Title', 'Reco_ID'])

start_time = time()
i = 0
no_response_ids = []
for item_id in ids:
    try:
        if item_id not in anime_recs.ID.tolist():
            titles, mal_ids = get_recs(item_id)
            for i in range(7):
                anime_recs.loc[len(anime_recs.index)] = [item_id, titles[i], mal_ids[i]]
            if len(anime_recs) % 100 == 0:
                print(len(anime_recs))
            sleep(2)
        if item_id in anime_recs.ID.tolist():
            continue
    except jp.APIException:
        no_response_ids.append(item_id)
        sleep(60)
print("--- %s seconds ---" % (time() - start_time))

anime_recs.to_csv('./datasets/anime_dataset/recommendations.csv')
print(anime_recs.head())
