import random
from recommender.models import Movie

def get_random_recommendation(recommendation_amount):
    all_ids = list(Movie.objects.values_list('movie_id', flat=True))
    if len(all_ids) < recommendation_amount:
        return all_ids

    return random.sample(all_ids, recommendation_amount)