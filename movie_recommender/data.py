import os

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from movie_recommender.settings import BASE_DIR

class Data:
    instance = None

    additional_data_df = None

    genre_cosine_similarity_matrix = None
    collaborators_cosine_similarity_matrix = None

    def load_data(self):
        self.additional_data_df = pd.read_csv(os.path.join(BASE_DIR, "datasets/additional_data.csv"))

        self.additional_data_df["names"] = self.additional_data_df["names"].apply(
            lambda x: x if pd.notna(x) else ["NO_DATA_AVAILABLE"])
        self.additional_data_df["genres"] = self.additional_data_df["genres"].apply(
            lambda x: x if pd.notna(x) else ["NO_DATA_AVAILABLE"]
        )

    def precompute(self):
        self.load_data()
        self.genre_cosine_similarity_matrix = self.calculate_cosine_similarity_matrix("genres")
        self.collaborators_cosine_similarity_matrix = self.calculate_cosine_similarity_matrix("names")

    def calculate_cosine_similarity_matrix(self, attr):
        if self.additional_data_df is None:
            raise Exception("Movies data not loaded")

        # generate a matrix of size #movies x #genres
        # it contains 0 and 1 indicating whether the genre applies to the movie
        mlb = MultiLabelBinarizer()
        matrix = mlb.fit_transform(self.additional_data_df[attr])

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


