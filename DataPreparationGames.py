import pandas as pd
from time import time
import DataPreparation as dp
from sklearn.preprocessing import OrdinalEncoder
from sklearn.impute import KNNImputer, SimpleImputer

games_dataset = pd.read_csv('./datasets/games_dataset/new_games_dataset.csv', low_memory=False)
# так как с самого начала, они распределены в хаотичном порядке, хочется сортировки...
games_dataset = games_dataset.sort_values(by='id', ignore_index=True)

# их можно удалить, так как по тем или иным причинам, они посчитались мной бесполезными
dropped_cols = ['aggregated_rating', 'aggregated_rating_count', 'game_engines', 'status', 'release_dates',
                'age_ratings', 'dlcs', 'franchise', 'parent_game', 'websites', 'external_games', 'alternative_names']
for col in dropped_cols:
    del games_dataset[col]

# так как нам нужны только те, у кого есть похожие объекты
# != game_modes, так как каким-то образом, просочились столбцы и теперь они в виде значений
# slug, так как единственное значение, которого не было
games_dataset = games_dataset.loc[(games_dataset.similar_games.isnull() == False)
                                  & (games_dataset.slug.isnull() == False)
                                  & (games_dataset.game_modes != 'game_modes')]

# так как коллекции - по сути, сборки игр, то можно присвоить пропущенным значениям их названия
games_dataset = games_dataset.fillna(value={'collection': games_dataset.name})

imputer = KNNImputer()

# здесь можно применить KNN, так как столбцы числовые
start_time = time()
impute_cols = ['first_release_date', 'rating', 'rating_count', 'total_rating', 'total_rating_count']
games_dataset[impute_cols] = imputer.fit_transform(games_dataset[impute_cols])
print('--- %s seconds ---' % (time() - start_time))

# переводим столбцы в их настоящие типы данных
num_cols = ['id', 'category', 'first_release_date', 'rating_count', 'total_rating_count', 'updated_at']
for num_col in num_cols:
    games_dataset[num_col] = games_dataset[num_col].astype('int64')

float_cols = ['rating', 'total_rating']
for float_col in float_cols:
    games_dataset[float_col] = games_dataset[float_col].astype('float64')

# так как не хочется, чтобы во всех столбцах были одинаковые значения, применяем такую технику
imputer = SimpleImputer(strategy='most_frequent')
for i in range(1, 160):
    games_dataset[:(i * 1000)] = imputer.fit_transform(games_dataset[:(i * 1000)])

# так как нам не важно, каким значением будет число
# лишь бы оно было разное, выбираем самый простой кодировщик
encoder = OrdinalEncoder()

# три последних кодируем, так как в них сравнительно мало уникальных значений
cat_cols = ['collection', 'game_modes', 'platforms', 'player_perspectives', 'genres']
games_dataset[cat_cols] = encoder.fit_transform(games_dataset[cat_cols])

# все те же словари, которые дадут нам возможность получить название по id и наоборот
ids = games_dataset.id
names = games_dataset.name
game_id_name = dict(zip(ids, names))
game_name_id_ = dict(zip(names, ids))

# применяем bag-of-words на текстовые столбцы, если что, то функция сама их найдет
games_vector = dp.implement_vectorizer(games_dataset)

# применяем масштабирование
scaled_nums, cols = dp.implement_scalar(games_dataset)
games_dataset[cols] = scaled_nums
