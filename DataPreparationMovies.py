import pandas as pd
import DataPreparation as dp
from sklearn.preprocessing import OrdinalEncoder


movies_dataset = pd.read_csv('./datasets/movies_dataset/movies_clear.csv')
print('Dataset Loaded...')

print('Start impute missing values...')
# таким образом, у нас получается так, что текстовые столбцы тоже заменяются средним значением
movies_dataset = movies_dataset.fillna(movies_dataset.mode().iloc[0])
print('End of imputation...')

print('Start encoding categorical values...')
# так как нам не важно, каким значением будет число
# лишь бы оно было разное, выбираем самый простой кодировщик
encoder = OrdinalEncoder()

# тут тоже, что и во всех других - слишком мало уникальных значений
cat_cols = ['original_language', 'status', 'spoken_languages', 'production_countries']
movies_dataset[cat_cols] = encoder.fit_transform(movies_dataset[cat_cols])
print('End of encoding...')

print('Start of transforming date column...')
# преобразовываем столбцы с датами в отдельные столбцы
cols = ['release_year', 'release_day', 'release_month']
splitted_data = movies_dataset.release_date.str.split('-')
date_cols = dp.date_to_cols(splitted_data, cols=cols)
movies_dataset[cols] = date_cols
del movies_dataset['release_date']
print('End of transformation...')

print('Make dict of names and IDs, IDs and names...')
# все те же словари, которые дадут нам возможность получить название по id и наоборот
ids = movies_dataset.id
names = movies_dataset.title
movie_id_name = dict(zip(ids, names))
movie_name_id = dict(zip(names, ids))
print('End of making dicts...')

print('Start transform text values into a Bag-Of-Words...')
# применяем bag-of-words на текстовые столбцы
movies_matrices = dp.implement_vectorizer(movies_dataset)
print('End of transformation...')

print('Implementing Normalization...')
# применяем масштабирование
scaled_nums, cols = dp.implement_scalar(movies_dataset)
movies_dataset[cols] = scaled_nums
print('End of Normalization...')

