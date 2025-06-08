import os

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer

path = "./datasets"

class Data:
    instance = None

    movies_df = None
    additional_data_df = None
    movies_with_people_df = None

    genre_cosine_similarity_matrix = None
    collaborators_cosine_similarity_matrix = None

    def load_data(self):
        self.movies_df = pd.read_csv(f"{path}/ml-20m/movies.csv")
        self.movies_df['genres'] = self.movies_df['genres'].apply(lambda x: x.split('|'))

        self.additional_data_df = pd.read_csv("./datasets/additional_data.csv")

        self.movies_with_people_df = pd.merge(self.movies_df, self.additional_data_df, how='left', on='movieId')
        self.movies_with_people_df["names"] = self.movies_with_people_df["names"].apply(
            lambda x: x if pd.notna(x) else ["NO_DATA_AVAILABLE"])

    def precompute(self):
        self.load_data()
        self.genre_cosine_similarity_matrix = self.calculate_cosine_similarity_matrix("genres")
        self.collaborators_cosine_similarity_matrix = self.calculate_cosine_similarity_matrix("names")

    def calculate_cosine_similarity_matrix(self, attr):
        if self.movies_with_people_df is None:
            raise Exception("Movies data not loaded")

        # generate a matrix of size #movies x #genres
        # it contains 0 and 1 indicating whether the genre applies to the movie
        mlb = MultiLabelBinarizer()
        matrix = mlb.fit_transform(self.movies_with_people_df[attr])

        # generate a matrix of size #movies x #movies
        # it contains the similarity-values for every movie combination
        return cosine_similarity(matrix)

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(Data, cls).__new__(cls)
            cls.instance._initialized = False

        return cls.instance

    def __init__(self, *args, **kwargs):
        if self._initialized:
            return
        self.precompute()
        self._initialized = True


