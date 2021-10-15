import pandas as pd
from numpy import where, all
from sklearn.metrics.pairwise import cosine_similarity


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
        return None


# функция, которая возвращает рекомендации
def give_recommendations(item: str, item_type: str = 'games'):
    if item_type == 'games':
        # так, это было сделано, так как иначе возникает конфликт между похожими файлами
        import DataPreparationGames as dpg
        games_matrix = pd.read_csv('./datasets/games_dataset/games_matrix.csv')
        game_id_name, game_name_id = dpg.data_preparation_for_games(True)

        full_cs = get_cosine_sim(games_matrix, None)
        similar = get_similar(full_cs, item, game_id_name, game_name_id)
        return similar
    if item_type == 'anime':
        import DataPreparationAnime as dpa
        anime_num_matrix = pd.read_csv('./datasets/anime_dataset/anime_num_matrix.csv')
        anime_text_matrix = pd.read_csv('./datasets/anime_dataset/anime_text_matrix.csv')

        full_cs = get_cosine_sim(anime_num_matrix, anime_text_matrix)
        similar = get_similar(full_cs, item, dpa.an_id_name_dict_jap, dpa.an_name_id_dict_jap)
        return similar
    if item_type == 'movies':
        import DataPreparationMovies as dpm
        movie_num_matrix = pd.read_csv('./datasets/movies_dataset/movies_num_matrix.csv')
        movie_text_matrix = pd.read_csv('./datasets/movies_dataset/movies_text_matrix.csv')

        full_cs = get_cosine_sim(movie_num_matrix, movie_text_matrix)
        similar = get_similar(full_cs, item, dpm.movie_id_name, dpm.movie_name_id)
        return similar
    else:
        print('This type of recommendations don`t in our database.')
        return None
