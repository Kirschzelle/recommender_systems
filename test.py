import time

from movie_recommender.algorithms.recommendation_collaborators import recommendation_collaborators
from movie_recommender.algorithms.recommendation_genres import recommendation_genres
from movie_recommender.extract_information_from_json_to_csv import extract_information_from_json_to_csv

from movie_recommender.data import Data

def main():
    start = time.time()
    extract_information_from_json_to_csv("./movie_recommender/datasets/extracted_content_ml-latest")
    end = time.time()
    print(end-start)

    while True:
        start = time.time()
        data = Data()
        end = time.time()
        print(end - start)

        i = int(input("Please enter movie ID: "))
        start = time.time()
        print(recommendation_genres(i, 10, data))
        end = time.time()
        print(end - start)

        print("\n")

        start = time.time()
        print(recommendation_collaborators(i, 10, data))
        end = time.time()
        print(end - start)

if __name__ == '__main__':
    main()