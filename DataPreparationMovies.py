import pandas as pd
import DataPreparation as dp
from sklearn.preprocessing import OrdinalEncoder


movies_dataset = pd.read_csv('./datasets/movies_dataset/movies_clear.csv')

# так как нам не важно, каким значением будет число
# лишь бы оно было разное, выбираем самый простой кодировщик
encoder = OrdinalEncoder()

# тут тоже, что и с прошлым набором
cat_cols = ['original_language', 'status', 'spoken_languages', 'production_countries']
movies_dataset[cat_cols] = encoder.fit_transform(movies_dataset[cat_cols])

movies_dataset = movies_dataset.fillna(movies_dataset.mode().iloc[0])

# преобразовываем столбцы с датами в отдельные столбцы
cols = ['release_year', 'release_day', 'release_month']
splitted_data = movies_dataset.release_date.str.split('-')
date_cols = dp.date_to_cols(splitted_data, cols=cols)
movies_dataset[cols] = date_cols
del movies_dataset['release_date']

ids = movies_dataset.id
names = movies_dataset.title
movie_id_name = dict(zip(ids, names))
movie_name_id = dict(zip(names, ids))

movies_matrices = dp.implement_vectorizer(movies_dataset)

scaled_nums, cols = dp.implement_scaler(movies_dataset)
movies_dataset[cols] = scaled_nums
