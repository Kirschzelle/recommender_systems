import os
import time

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer

movies_df = None
people_df = None
movies_with_people_df = None

genre_cosine_similarity_matrix = None
collaborators_cosine_similarity_matrix = None

# preloads all files needed
def load_data():
    global movies_df
    movies_df = pd.read_csv("./ml-20m/movies.csv")
    movies_df['genres'] = movies_df['genres'].apply(lambda x: x.split('|'))

    global people_df
    people_df = pd.read_csv("output.csv")

    global movies_with_people_df
    movies_with_people_df = pd.merge(movies_df, people_df, how='left', on='movieId')
    movies_with_people_df["names"] = movies_with_people_df["names"].apply(lambda x: ["NO_DATA_AVAILABLE"] if pd.isna(x) else x)

def precompute():
    load_data()
    global genre_cosine_similarity_matrix
    genre_cosine_similarity_matrix = calculate_cosine_similarity_matrix("genres")
    global collaborators_cosine_similarity_matrix
    collaborators_cosine_similarity_matrix = calculate_cosine_similarity_matrix("names")

def calculate_cosine_similarity_matrix(attr):
    if movies_with_people_df is None:
        raise Exception("Movies data not loaded")

    # generate a matrix of size #movies x #genres
    # it contains 0 and 1 indicating whether the genre applies to the movie
    mlb = MultiLabelBinarizer()
    matrix = mlb.fit_transform(movies_with_people_df[attr])

    # generate a matrix of size #movies x #movies
    # it contains the similarity-values for every movie combination
    return cosine_similarity(matrix)

# extracts the needed informations from all json-files
def extract_information_from_json_to_csv():
    # create a new dataframe for the results
    df = pd.DataFrame(columns = ['movieId', 'names'])
    # iterate through the json-files
    for filename in os.listdir("./extracted_content_ml-latest"):
        if filename.endswith(".json"):
            movie_id = filename.split('.')[0]
            one_movie_metadata_df = pd.read_json(f"./extracted_content_ml-latest/{filename}")

            # checks to determine which databases have informations about this movie saved.
            # The primary source for the people working on a movie is tmdb and the secondary movielens.
            # imdb does not provide usable informations for the collaborating-people-recommendation-strategy.
            names = []
            if one_movie_metadata_df.__contains__("tmdb"):
                credits = one_movie_metadata_df["tmdb"]["credits"]

                cast = credits.get("cast")
                for i in range(len(cast)):
                    names.append(cast[i].get("name"))

                crew = credits.get("crew")
                for i in range(len(crew)):
                    names.append(crew[i].get("name"))

            elif one_movie_metadata_df.__contains__("movielens"):
                people = one_movie_metadata_df["movielens"]["directors"]
                people.extend(one_movie_metadata_df["movielens"]["actors"])
                names = people

            else:
                print("ERROR")

            # remove all duplicate names
            names = list(dict.fromkeys(names))


            """
            Here other types of information can be extracted. To add columns just add the column name above, 
            and add the informations to the DataFrame below
            """

            # only add the rows with more than zero actors to the DataFrame
            if len(names) != 0:
                df.loc[len(df)] = {"movieId": movie_id, "names": names}

    # converts the DataFrame to a csv-file
    df.to_csv("output.csv", index=False)

if __name__ == "__main__":
    start = time.time()
    extract_information_from_json_to_csv()
    end = time.time()

    elapsed = end - start
    hours, remaining = divmod(elapsed, 3600)
    minutes, seconds = divmod(remaining, 60)
    print(f"Time elapsed: {hours:02}:{minutes:02}:{seconds:02}")