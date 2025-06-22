import os

from django.apps import AppConfig
from extract_information_from_json_to_csv import extract_information_from_json_to_csv
from movie_recommender.settings import BASE_DIR
from data import Data

class RecommenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommender'

    def ready(self):
        if not os.path.exists(os.path.join(BASE_DIR, "datasets/additional_data.csv")):
            extract_information_from_json_to_csv(os.path.join(BASE_DIR, "datasets/information"))
        data = Data()