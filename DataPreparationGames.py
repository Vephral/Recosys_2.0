import pandas as pd
from time import time
# в нем находятся все нужные нам библиотеки и функции
import DataPreparation as dp
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import MinMaxScaler, OrdinalEncoder

games_dataset = pd.read_csv('./datasets/games_dataset/new_games_dataset.csv', low_memory=False)
# так как с самого начала, они распределены в хаотичном порядке
games_dataset = games_dataset.sort_values(by='id', ignore_index=True)

imputer = KNNImputer()
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

# так как нам не важно, каким значением будет число
# лишь бы оно было разное, выбираем самый простой кодировщик
encoder = OrdinalEncoder()

# три последних кодируем, так как в них сравнительно мало уникальных значений
cat_cols = ['collection', 'game_modes', 'platforms', 'player_perspectives', 'genres']
games_dataset[cat_cols] = encoder.fit_transform(games_dataset[cat_cols])

ids = games_dataset.id
names = games_dataset.name
game_id_name = dict(zip(ids, names))
game_name_id_ = dict(zip(names, ids))

games_vector = dp.implement_vectorizer(games_dataset)

scaled_nums, cols = dp.implement_scaler(games_dataset)
games_dataset[cols] = scaled_nums