from extract_information_from_json_to_csv import extract_information_from_json_to_csv

from strategies.recommendation_collaborators import recommendation_collaborators
from data import Data
from strategies.recommendation_genres import recommendation_genres

extract_information_from_json_to_csv("./datasets/extracted_content_ml-latest")

data = Data()

print(recommendation_genres(1,10,data))

print("\n")

print(recommendation_collaborators(1,10,data))