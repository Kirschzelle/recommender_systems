import os

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer

class Data:
    instance = None

    movies_df = None
    people_df = None
    movies_with_people_df = None

    genre_cosine_similarity_matrix = None
    collaborators_cosine_similarity_matrix = None

    def load_data(self):
        self.movies_df = pd.read_csv("./datasets/ml-20m/movies.csv")
        self.movies_df['genres'] = self.movies_df['genres'].apply(lambda x: x.split('|'))

        self.people_df = pd.read_csv("output.csv")

        self.movies_with_people_df = pd.merge(self.movies_df, self.people_df, how='left', on='movieId')
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

    # extracts the needed informations from all json-files
    def extract_information_from_json_to_csv(self):
        # iterate through the json-files
        rows = []
        for filename in os.listdir("./datasets/extracted_content_ml-latest"):
            if filename.endswith(".json"):
                movie_id = filename.split('.')[0]
                one_movie_metadata_df = pd.read_json(f"./datasets/extracted_content_ml-latest/{filename}")

                # checks to determine which databases have informations about this movie saved.
                # The primary source for the people working on a movie is tmdb and the secondary movielens.
                # imdb does not provide usable informations for the collaborating-people-recommendation-strategy.
                names = []
                if one_movie_metadata_df.__contains__("tmdb"):
                    credits = one_movie_metadata_df["tmdb"]["credits"]

                    cast = credits["cast"]
                    for i in range(len(cast)):
                        names.append(cast[i].get("name"))

                    crew = credits["crew"]
                    for i in range(len(crew)):
                        names.append(crew[i].get("name"))

                elif one_movie_metadata_df.__contains__("movielens"):
                    people = one_movie_metadata_df["movielens"]["directors"]
                    people.extend(one_movie_metadata_df["movielens"]["actors"])
                    names = people

                # remove all duplicate names
                names = list(dict.fromkeys(names))

                """
                Here other types of information can be extracted. 
                """

                # only add the rows with more than zero actors
                if len(names) != 0:
                    rows.append({"movieId": movie_id, "names": names})

        # create a new DataFrame for the results
        df = pd.DataFrame(rows, columns=['movieId', 'names'])
        # converts the DataFrame to a csv-file
        df.to_csv("datasets/output.csv", index=False)

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


