from numpy import where
from sklearn.metrics.pairwise import cosine_similarity


def get_cosine_sim(text_matrix, num_matrix):
    text_cs = cosine_similarity(text_matrix)
    num_cs = cosine_similarity(num_matrix)
    full_cs = (num_cs + text_cs) / 2
    return full_cs


def get_similar(full_cs, item, id_dict, name_dict):
    # пока что без упоминания конретного словаря
    # потом будет ветвление
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
