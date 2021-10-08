import re
import numpy as np
import pandas as pd
from time import time
from random import randint
from collections import Counter
from urlextract import URLExtract
from scipy.sparse import csr_matrix
from sklearn.pipeline import Pipeline
from nltk.stem.porter import PorterStemmer
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler, OrdinalEncoder


# ради того, чтобы быть для всех,
# эта функция усложнилась
def date_to_cols(series, cols):
    new_series = pd.Series(dtype='int64')
    for i in range(len(cols)):
        col = []
        for data in series:
            try:
                # если не получается преобразовать, значит
                # объект - пропущенное значение
                col.append(int(data[i]))
            except:
                # а если объект - пропущенное значение
                # то можно выбрать рандомное значение, просто чтобы все работало
                if i == 0 or i == 3:
                    col.append(randint(0, 12))
                if i == 1 or i == 4:
                    col.append(randint(0, 31))
                if i == 2 or i == 5:
                    col.append(randint(1958, 2021))
        new_series[cols[i]] = col
    return new_series


anime_dataset = pd.read_csv('./datasets/anime_dataset/anime.csv')
games_dataset = pd.read_csv('./datasets/games_dataset/new_games_dataset.csv', low_memory=False)
movies_dataset = pd.read_csv('./datasets/movies_dataset/movies_clear.csv')

games_dataset = games_dataset.sort_values(by='id', ignore_index=True)

imputer = KNNImputer()
dropped_cols = ['aggregated_rating', 'aggregated_rating_count', 'game_engines', 'status', 'release_dates',
                'age_ratings', 'dlcs', 'franchise', 'parent_game', 'websites', 'external_games', 'alternative_names']

for col in dropped_cols:
    del games_dataset[col]

# так как нам нужны только те, у кого есть похожие объекты
# != game_modes, так как каким-то образом, просочились столбцы и теперь они ввиде значений
# slug, так как единственное значение, которого не было
games_dataset = games_dataset.loc[(games_dataset.similar_games.isnull() == False)
                                  & (games_dataset.slug.isnull() == False)
                                  & (games_dataset.game_modes != 'game_modes')]

# так как коллекции - по сути, сборки игр, то можно присвоить пропущенным значениям их названия
games_dataset = games_dataset.fillna(value={'collection': games_dataset.name})

impute_cols = ['first_release_date', 'rating', 'rating_count', 'total_rating', 'total_rating_count']

start_time = time()
games_dataset[impute_cols] = imputer.fit_transform(games_dataset[impute_cols])
print('--- %s seconds ---' % (time() - start_time))

num_cols = ['id', 'category', 'first_release_date', 'rating_count', 'total_rating_count', 'updated_at']
for num_col in num_cols:
    games_dataset[num_col] = games_dataset[num_col].astype('int64')

float_cols = ['rating', 'total_rating']
for float_col in float_cols:
    games_dataset[float_col] = games_dataset[float_col].astype('float64')

imputer = SimpleImputer(strategy='most_frequent')
for i in range(1, 160):
    games_dataset[:(i * 1000)] = imputer.fit_transform(games_dataset[:(i * 1000)])

movies_dataset = movies_dataset.fillna(movies_dataset.mode().iloc[0])

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

# три последних кодируем, так как в них сравнительно мало уникальных значений
cat_cols = ['collection', 'game_modes', 'platforms', 'player_perspectives', 'genres']
games_dataset[cat_cols] = encoder.fit_transform(games_dataset[cat_cols])

# тут тоже, что и с прошлым набором
cat_cols = ['original_language', 'status', 'spoken_languages', 'production_countries']
movies_dataset[cat_cols] = encoder.fit_transform(movies_dataset[cat_cols])

# и тут
cat_cols = ['Type', 'Duration', 'Rating', 'Source', 'Studios', 'Premiered', 'Episodes', 'Producers', 'Licensors']
anime_dataset[cat_cols] = encoder.fit_transform(anime_dataset[cat_cols])

cols = ['release_year', 'release_day', 'release_month']
splitted_data = movies_dataset.release_date.str.split('-')
date_cols = date_to_cols(splitted_data, cols=cols)
movies_dataset[cols] = date_cols
del movies_dataset['release_date']

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
date_cols = date_to_cols(replaced_date, cols=cols)
anime_dataset[cols] = date_cols
del anime_dataset['Aired']


def remove_punctuation(str, list):
    for sign in list:
        str = str.replace(sign, '')
    return str


def remove_html_tags(str):
    html_tag = ''
    new_str = str
    start = False
    for i in range(len(str)):
        if str[i] == '<':
            html_tag += str[i]
            start = True
        if start and str[i] != '<':
            html_tag += str[i]
        if str[i] == '>':
            start = False
            new_str = new_str.replace(html_tag, '')
            html_tag = ''
    return new_str


class TextToVectorCounter(BaseEstimator, TransformerMixin):
    def __init__(self, to_lower=True, remove_punctuation=True, stemming=True, replace_nums=True,
                 replace_urls=True, remove_html_tags=True):
        self.to_lower = to_lower
        self.remove_punctuation = remove_punctuation
        self.replace_nums = replace_nums
        self.replace_urls = replace_urls
        self.stemming = stemming
        self.remove_html_tags = remove_html_tags

    def fit(self, dataset, label=None):
        return self

    def transform(self, dataset, label=None):
        vector = []
        for text in dataset:
            if self.to_lower:
                text = text.lower()
            if self.replace_urls:
                list_of_urls = URLExtract().find_urls(text)
                for url in list_of_urls:
                    text = text.replace(url, 'URL')
            if self.remove_punctuation:
                text = remove_punctuation(text, ['.', ',', '?', ':', ';', '[', ']',
                                                 '!', '(', ')', '-', "'", '}', '{'])
            if self.replace_nums:
                text = re.sub(r'\d+(?:\.\d*)?(?:[eE][+-]?\d+)?', 'NUMBER', text)
            if self.remove_html_tags:
                text = remove_html_tags(text)
            # так будет быстрее, за счет меньшего количества операций
            words_count = Counter(text.split())
            if self.stemming:
                stemmed_words = {}
                for word, count in words_count.items():
                    stemmed_word = PorterStemmer().stem(word)
                    stemmed_words[stemmed_word] = count
                words_count = stemmed_words
            vector.append(words_count)
        return vector


class VectorCounterToFeature(BaseEstimator, TransformerMixin):
    def __init__(self, vocabulary_size=1000):
        self.vocab_size = vocabulary_size

    def fit(self, dataset, label=None):
        # все ради сокращения кода и функции most_common
        total_counts = Counter()
        self.vocabulary = {}
        for data in dataset:
            for word, count in data.items():
                # кажется, что бессмысленно
                # но на самом деле мы в одном словаре собираем все словари
                # а минимальное - для того, чтобы не было разброса данных
                total_counts[word] += min(count, 10)
        # так как иначе можно получить бесконечную матрицу признаков.
        # а так у нас установленное значение
        most_common = total_counts.most_common()[:self.vocab_size]
        for index, word in enumerate(most_common):
            self.vocabulary[word[0]] = index
        return self

    def transform(self, dataset, label=None):
        rows = []
        data = []
        cols = []
        # на вход попадает total_counts из метода fit
        # enumerate для того, чтобы содержать количество итераций
        # в общем, равносильно обычному счетчику, но для итерируемого объекта
        for row, word_counts in enumerate(dataset):
            # если что, то за счет именно функции get мы получаем матрицу с нулями
            for word, count in word_counts.items():
                rows.append(row)
                # если ничего не нашлось, то 0
                cols.append(self.vocabulary.get(word, 0))
                # в каждом элементе строки у нас будут числа
                # означающие количество появлений слова
                data.append(count)
        return csr_matrix((data, (rows, cols)), shape=(len(dataset), self.vocab_size + 1))


text_to_nums = Pipeline([('TextToCounter', TextToVectorCounter()),
                         ('CounterToFeature', VectorCounterToFeature())], verbose=True)


def implement_vectorizer(dataset):
    list_of_matrices = []
    text_cols = [i for i in dataset.columns if dataset[i].dtype == 'object']
    for col in text_cols:
        list_of_matrices.append(text_to_nums.fit_transform(dataset[col]))
    return list_of_matrices


ids = games_dataset.id
names = games_dataset.name
game_id_name = dict(zip(ids, names))
game_name_id_ = dict(zip(names, ids))

games_vector = implement_vectorizer(games_dataset)

ids = movies_dataset.id
names = movies_dataset.title
movie_id_name = dict(zip(ids, names))
movie_name_id = dict(zip(names, ids))

movies_matrices = implement_vectorizer(movies_dataset)

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

anime_matrices = implement_vectorizer(anime_dataset)

scaler = MinMaxScaler()


def implement_scaler(dataset):
    num_cols = [i for i in dataset.columns if dataset[i].dtype != 'object' and i not in ['MAL_ID', 'id']]
    scaled_cols = scaler.fit_transform(dataset[num_cols])
    return scaled_cols, num_cols


scaled_nums, cols = implement_scaler(games_dataset)
games_dataset[cols] = scaled_nums

scaled_nums, cols = implement_scaler(movies_dataset)
movies_dataset[cols] = scaled_nums

scaled_nums, cols = implement_scaler(anime_dataset)
anime_dataset[cols] = scaled_nums
