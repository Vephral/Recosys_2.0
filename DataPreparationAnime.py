import numpy as np
import pandas as pd
import DataPreparation as dp
from sklearn.impute import KNNImputer
from sklearn.preprocessing import OrdinalEncoder

anime_dataset = pd.read_csv('./datasets/anime_dataset/anime.csv')

# все столбцы, которые назваются Score
scores = [i for i in anime_dataset.columns if i.split('-')[0] == 'Score']
anime_dataset[scores] = anime_dataset[scores].replace('Unknown', '0')
anime_dataset[scores] = anime_dataset[scores].astype('float64')

imputer = KNNImputer()

# из-за того, что в наборе были скрытые пропущенные значения,
# пришлось их "выпустить"
anime_dataset['Episodes'] = anime_dataset.Episodes.replace('Unknown', np.NaN)
anime_dataset['Ranked'] = anime_dataset.Ranked.replace('Unknown', np.NaN)
anime_dataset[['Episodes', 'Ranked']] = imputer.fit_transform(anime_dataset[['Episodes', 'Ranked']])

# так как нам не важно, каким значением будет число
# лишь бы оно было разное, выбираем самый простой кодировщик
encoder = OrdinalEncoder()

# все эти столбцы - категорические, так как содержат сравнительно маленькое количество уникальных значений
cat_cols = ['Type', 'Duration', 'Rating', 'Source', 'Studios', 'Premiered', 'Episodes', 'Producers', 'Licensors']
anime_dataset[cat_cols] = encoder.fit_transform(anime_dataset[cat_cols])

# самый простой способ
cleared_date = anime_dataset.Aired.str.replace(',', '')
# regex=false, иначе питончик будет ругаться
cleared_date = cleared_date.str.replace('?', 'Unknown', regex=False)
# ебаные to, наконец-то, удалены
cleared_date = cleared_date.str.replace('to', '')
# ссаный jupyter ещё не поддерживает 10 версию, поэтому здесь костыли
# вместо нормальных case/switch
replaced_date = []
for date in cleared_date:
    das = date.split()
    # с самого начала задумывалось, что затем строки будут
    # переводиться в числа и так будет проверяться пропущенность значений.
    # Все так и было. Инфа сотка.
    for i in range(len(das)):
        if das[i] == 'Jan':
            date = date.replace(das[i], '01')
        if das[i] == 'Feb':
            date = date.replace(das[i], '02')
        if das[i] == 'Mar':
            date = date.replace(das[i], '03')
        if das[i] == 'Apr':
            date = date.replace(das[i], '04')
        if das[i] == 'May':
            date = date.replace(das[i], '05')
        if das[i] == 'Jun':
            date = date.replace(das[i], '06')
        if das[i] == 'Jul':
            date = date.replace(das[i], '07')
        if das[i] == 'Aug':
            date = date.replace(das[i], '08')
        if das[i] == 'Sep':
            date = date.replace(das[i], '09')
        if das[i] == 'Oct':
            date = date.replace(das[i], '10')
        if das[i] == 'Nov':
            date = date.replace(das[i], '11')
        if das[i] == 'Dec':
            date = date.replace(das[i], '12')
    replaced_date.append(date)

# надо же как-то все это разделить
replaced_date = pd.Series(replaced_date).str.split()

cols = ['release_month', 'release_day', 'release_year', 'end_month', 'end_day', 'end_year']
date_cols = dp.date_to_cols(replaced_date, cols=cols)
anime_dataset[cols] = date_cols
del anime_dataset['Aired']
# как мне кажется, от японского названия нет толку, поэтому просто удалим его.
del anime_dataset['Japanese name']

# разделение для того, чтобы, ну кто знает этих людей, вдруг кому-то придет в голову кинуть название на английском языке
ids = anime_dataset.MAL_ID
jap_names = anime_dataset.Name
en_names = anime_dataset['English name']
an_id_name_dict_jap = dict(zip(ids, jap_names))
an_id_name_dict_en = dict(zip(ids, en_names))
an_name_id_dict_jap = dict(zip(jap_names, ids))
an_name_id_dict_en = dict(zip(en_names, ids))

# кодируем текстовые столбцы в матрицу признаков
anime_matrices = dp.implement_vectorizer(anime_dataset)

# применяем масштабирование на всех столбцах
scaled_nums, cols = dp.implement_scalar(anime_dataset)
anime_dataset[cols] = scaled_nums
