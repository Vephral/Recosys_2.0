import pandas as pd
from numpy import where, all
from sklearn.metrics.pairwise import cosine_similarity
from DataPreparationGames import game_name_id, game_id_name

# функция, которая вычисляет схожесть между элементами в наборе данных
def get_cosine_sim(num_matrix, text_matrix):
    if all(text_matrix is not None):
        text_cs = cosine_similarity(text_matrix)
        num_cs = cosine_similarity(num_matrix)
        full_cs = (num_cs + text_cs) / 2
    else:
        full_cs = cosine_similarity(num_matrix)
    return full_cs


# функция, которая получает названия похожих объектов, а словари нужны для того, чтобы функция была универсальной
def get_similar(full_cs, item, id_dict, name_dict):
    if item in name_dict.keys():
        similar = []
        item_id = name_dict[item]
        sorted_full_cs = sorted(full_cs[item_id], reverse=True)
        similar_values = sorted_full_cs[1:8]
        for value in similar_values:
            similar_index = where(full_cs[item_id] == value)
            similar.append(id_dict[int(similar_index[0])])
        return similar
    else:
        print('Title not in our database or it`s invalid.')


# функция, которая возвращает рекомендации
def give_recommendations(item: str, reco_type='normal'):
    games_matrix = pd.read_csv('./datasets/games_dataset/games_matrix.csv')
    game_id_name, game_name_id = g

    full_cs = get_cosine_sim(games_matrix, None)
    similar = get_similar(full_cs, item, game_id_name, game_name_id)

    if reco_type == 'normal':
        [print(i, ' - ', similar[i]) for i in range(len(similar))]
    if reco_type == 'vk':
        # здесб будет код, который обращается к вк
        print(similar)
