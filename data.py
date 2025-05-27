import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer

movies_df = None
cosine_similarity_matrix = None

# preloads all files needed
def load_data():
    global movies_df
    movies_df = pd.read_csv("./ml-20m/movies.csv")
    movies_df['genres'] = movies_df['genres'].apply(lambda x: x.split('|'))

def calculate_cosine_similarity_matrix():
    if movies_df is None:
        raise Exception("Movies data not loaded")
    # generate a matrix of size #movies x #genres
    # it contains 0 and 1 indicating whether the genre applies to the movie
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(movies_df['genres'])

    # generate a matrix of size #movies x #movies
    # it contains the similarity-values for every movie combination
    global cosine_similarity_matrix
    cosine_similarity_matrix = cosine_similarity(genre_matrix)

def precompute():
    load_data()
    calculate_cosine_similarity_matrix()