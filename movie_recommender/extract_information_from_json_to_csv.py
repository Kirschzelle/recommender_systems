# extracts the needed informations from all json-files
import os
import pandas as pd

from movie_recommender.settings import BASE_DIR

def extract_information_from_json_to_csv(path):
    # iterate through the json-files
    rows = []
    for filename in os.listdir(path):
        if filename.endswith(".json"):
            movie_id = filename.split('.')[0]
            one_movie_metadata_df = pd.read_json(f"{path}/{filename}")

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

            genres = []
            if one_movie_metadata_df.__contains__("tmdb"):
                gs = one_movie_metadata_df["tmdb"]["genres"]
                genres = [genre.get("name") for genre in gs if genre.get("name")]

            elif one_movie_metadata_df.__contains__("imdb"):
                genres = one_movie_metadata_df["imdb"]["genres"]

            elif one_movie_metadata_df.__contains__("movielens"):
                genres = one_movie_metadata_df["movielens"]["genres"]


            """
            Here other types of information can be extracted. 
            """

            # only add the rows with more than zero actors
            if len(names) != 0:
                rows.append({"movieId": movie_id, "names": names, "genres": genres})

    # create a new DataFrame for the results
    df = pd.DataFrame(rows, columns=['movieId', 'names', 'genres'])
    # converts the DataFrame to a csv-file
    df.to_csv(os.path.join(BASE_DIR, "datasets/additional_data.csv"), index=False)