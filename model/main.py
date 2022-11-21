import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import CountVectorizer
import ast
from joblib import dump, load

data = pd.read_csv('data/titles.csv')

# remove all the rows where description is NaN
data_clean = data[data['description'].notna()]

dump(data_clean, '/model/data_clean.joblib') 

tf = TfidfVectorizer(analyzer='word', min_df=0, stop_words='english') #  ngram_range=(1, 3),
tfidf_matrix = tf.fit_transform(data_clean['description'])

# add the genres and production country as meta data

# go from list to string and remove spaces in genre names
def clean_list_data(g):
    s = ""
    for genre in ast.literal_eval(g):
        s += genre.replace(" ", "") + " "
        
    return s.rstrip()

count = CountVectorizer(stop_words='english')

data_clean_genres = data_clean['genres'].apply(clean_list_data)
count_genre = count.fit_transform(data_clean_genres)

data_clean_production_countries = data_clean['production_countries'].apply(clean_list_data)
count_production_countries = count.fit_transform(data_clean_production_countries)

# add this vector to the tfidf matrix
meta = np.hstack((tfidf_matrix.toarray(), count_genre.toarray(), count_production_countries.toarray()))

cosine_similarities = linear_kernel(meta, meta)

dump(cosine_similarities, '/model/cosine_similarities.joblib') 