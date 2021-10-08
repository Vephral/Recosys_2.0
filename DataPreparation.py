import re
import pandas as pd
from random import randint
from collections import Counter
from urlextract import URLExtract
from scipy.sparse import csr_matrix
from sklearn.pipeline import Pipeline
from nltk.stem.porter import PorterStemmer
from sklearn.preprocessing import MinMaxScaler
from sklearn.base import BaseEstimator, TransformerMixin


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


def remove_punctuation(string, signs):
    for sign in signs:
        string = string.replace(sign, '')
    return string


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

    def fit(self, dataset):
        return self

    def transform(self, dataset):
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
    def __init__(self, vocabulary_size: int = 1000):
        self.vocabulary = {}
        self.vocab_size = vocabulary_size

    def fit(self, dataset):
        # все ради сокращения кода и функции most_common
        total_counts = Counter()
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

    def transform(self, dataset):
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


scalar = MinMaxScaler()


def implement_scalar(dataset):
    num_cols = [i for i in dataset.columns if dataset[i].dtype != 'object' and i not in ['MAL_ID', 'id']]
    scaled_cols = scalar.fit_transform(dataset[num_cols])
    return scaled_cols, num_cols
