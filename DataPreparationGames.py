import pandas as pd
import DataPreparation as dp
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler

games_dataset = pd.read_csv('./datasets/games_dataset/new_games_dataset.csv', low_memory=False)
# так как с самого начала, они распределены в хаотичном порядке, хочется сортировки...
games_dataset = games_dataset.sort_values(by='id', ignore_index=True)
print('Dataset Loaded...')

# так как нам нужны только те, у кого есть похожие объекты
# != game_modes, так как каким-то образом, просочились столбцы и теперь они в виде значений
# slug, так как единственное значение, которого не было
games_dataset = games_dataset.loc[(games_dataset.similar_games.isnull() == False)
                                  & (games_dataset.slug.isnull() == False)
                                  & (games_dataset.game_modes != 'game_modes')]
# теперь, выберем только те объекты, которые будут нам полезны,
# так как в любом случае, набор слишком большой и не помещается в память.
games_dataset = games_dataset.loc[((games_dataset.category == '0')
                                   | (games_dataset.category == '8')
                                   | (games_dataset.category == '9')
                                   | (games_dataset.category == '11')) & (games_dataset.release_dates.isnull() == False)
                                  & (games_dataset.keywords.isnull() == False)]

print('Start impute missing values...')
# их можно удалить, так как по тем или иным причинам, они посчитались мной бесполезными
dropped_cols = ['aggregated_rating', 'aggregated_rating_count', 'game_engines', 'status', 'release_dates',
                'age_ratings', 'dlcs', 'franchise', 'parent_game', 'websites', 'external_games', 'alternative_names']
for col in dropped_cols:
    del games_dataset[col]

# так как коллекции - по сути, сборки игр, то можно присвоить пропущенным значениям их названия
games_dataset = games_dataset.fillna(value={'collection': games_dataset.name})

# здесь можно применить KNN, так как столбцы числовые
imputer = KNNImputer()
impute_cols = ['first_release_date', 'rating', 'rating_count', 'total_rating', 'total_rating_count']
games_dataset[impute_cols] = imputer.fit_transform(games_dataset[impute_cols])

# переводим столбцы в их настоящие типы данных
num_cols = ['id', 'category', 'first_release_date', 'rating_count', 'total_rating_count', 'updated_at']
for num_col in num_cols:
    games_dataset[num_col] = games_dataset[num_col].astype('int64')

float_cols = ['rating', 'total_rating']
for float_col in float_cols:
    games_dataset[float_col] = games_dataset[float_col].astype('float64')

# так как не хочется, чтобы во всех столбцах были одинаковые значения, применяем такую технику
imputer = SimpleImputer(strategy='most_frequent')
for i in range(50):
    games_dataset[(i * 1000):((i + 1) * 1000)] = imputer.fit_transform(games_dataset[(i * 1000):((i + 1) * 1000)])
print('End of imputation...')

print('Start encoding categorical values...')
# так как нам не важно, каким значением будет число
# лишь бы оно было разное, выбираем самый простой кодировщик
encoder = OrdinalEncoder()
# три последних кодируем, так как в них сравнительно мало уникальных значений
cat_cols = ['collection', 'game_modes', 'platforms', 'player_perspectives', 'genres', 'keywords', 'involved_companies']
games_dataset[cat_cols] = encoder.fit_transform(games_dataset[cat_cols])
print('End of encoding...')

print('Make dict of names and IDs, IDs and names...')
# если не обнулить индекс, то потом вылезут ошибки, связанные с индексом
games_dataset = games_dataset.reset_index(drop=True)
# все те же словари, которые дадут нам возможность получить название по id и наоборот
game_id_name, game_name_id = dp.make_dict_of_names(games_dataset, games_dataset.name)
print('End of making dicts...')

del games_dataset['id']
del games_dataset['name']
del games_dataset['slug']
del games_dataset['similar_games']

print('Implementing Normalization...')
scalar = MinMaxScaler()
games_dataset = scalar.fit_transform(games_dataset)
print('End of Normalization...')

# у данного набора тоже большое время ожидания исполнения кода - 3 минуты
games_dataset.to_csv('C:/Users/ASDW/PycharmProjects/Recosys 2.0/datasets/games_dataset/games_matrix.csv')
