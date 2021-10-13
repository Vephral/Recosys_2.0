import numpy as np
import pandas as pd
import DataPreparation as dp
from sklearn.impute import KNNImputer
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler

anime_dataset = pd.read_csv('./datasets/anime_dataset/anime.csv')
print('Dataset Loaded...')

print('Start impute missing values...')
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
print('End of imputation...')

print('Start encoding categorical values...')
# так как нам не важно, каким значением будет число
# лишь бы оно было разное, выбираем самый простой кодировщик
encoder = OrdinalEncoder()
# все эти столбцы - категорические, так как содержат сравнительно маленькое количество уникальных значений
cat_cols = ['Type', 'Duration', 'Rating', 'Source', 'Studios', 'Premiered', 'Episodes', 'Producers', 'Licensors']
anime_dataset[cat_cols] = encoder.fit_transform(anime_dataset[cat_cols])
print('End of encoding...')

print('Start of transforming date column...')
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
print('End of transformation...')

# как мне кажется, от японского названия нет толку, поэтому просто удалим его.
del anime_dataset['Japanese name']
del anime_dataset['Aired']

print('Make dict of names and IDs, IDs and names...')
# разделение для того, чтобы, ну кто знает этих людей, вдруг кому-то придет в голову кинуть название на английском языке
an_id_name_dict_jap, an_name_id_dict_jap = dp.make_dict_of_names(anime_dataset, anime_dataset.Name)
an_id_name_dict_en, an_name_id_dict_en =  dp.make_dict_of_names(anime_dataset, anime_dataset['English name'])
print('End of making dicts...')

# их удаляем, так как больше не понадобятся
del anime_dataset['MAL_ID']
del anime_dataset['Name']

print('Start transform text values into a Bag-Of-Words...')
text_cols = ['Genres', 'English name']
# кодируем текстовые столбцы в матрицу признаков
anime_dataset['text_features'] = dp.get_text_features(anime_dataset, text_cols)
#anime_matrix = dp.text_to_nums.fit_transform(anime_dataset['text_features'])
anime_matrix = pd.read_csv('./datasets/anime_dataset/anime_text_matrix.csv')
print('End of transformation...')

del anime_dataset['Genres']
del anime_dataset['English name']
del anime_dataset['text_features']

print('Implementing Normalization...')
# применяем масштабирование на всех столбцах
scalar = MinMaxScaler()
anime_dataset = scalar.fit_transform(anime_dataset)
print('End of Normalization...')

# это нужно сделать, так как большое время ожидания исполнения кода - 9 минут на то, чтобы преобразовать тексты
# но сейчас, когда уже все сделано, этот код не нужен
# anime_text_matrix = pd.DataFrame(anime_matrix.toarray())
# anime_text_matrix.to_csv('C:/Users/ASDW/PycharmProjects/Recosys 2.0/datasets/anime_dataset/anime_txt_matrix.csv')
# anime_dataset.to_csv('C:/Users/ASDW/PycharmProjects/Recosys 2.0/datasets/anime_dataset/anime_num_matrix.csv')
