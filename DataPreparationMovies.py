import pandas as pd
import DataPreparation as dp
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler

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
movie_id_name, movie_name_id = dp.make_dict_of_names(movies_dataset, movies_dataset.name)
print('End of making dicts...')

del movies_dataset['title']
del movies_dataset['id']

print('Start transform text values into a Bag-Of-Words...')
text_cols = ['genres', 'keywords', 'overview', 'production_companies', 'tagline', 'original_title']
movies_matrices = dp.get_text_features(movies_dataset, text_cols)
movies_dataset['text_features'] = dp.get_text_features(movies_dataset, text_cols)
movies_matrix = dp.text_to_nums.fit_transform(movies_dataset['text_features'])
text_cols.append('text_features')
print('End of transformation...')

# удаляем, так как больше они нам не нужны
for col in text_cols:
    del movies_dataset[col]

print('Implementing Normalization...')
scalar = MinMaxScaler()
movies_dataset = scalar.fit_transform(movies_dataset)
print('End of Normalization...')

movies_text_matrix = pd.DataFrame(movies_matrix.toarray())
movies_dataset.to_csv('C:/Users/ASDW/PycharmProjects/Recosys 2.0/datasets/movies_dataset/movies_num_matrix')
movies_text_matrix.to_csv('C:/Users/ASDW/PycharmProjects/Recosys 2.0/datasets/movies_dataset/movies_text_matrix.csv')
