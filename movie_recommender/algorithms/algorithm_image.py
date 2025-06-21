from recommender.models import MovieImageRecommendation
from django.conf import settings

def get_image_based_recommendation(movie_id, recommendation_amount=5):
    try:
        recs = MovieImageRecommendation.objects.get(movie__movie_id=movie_id)
        return recs.recommended_movies[:recommendation_amount]
    except MovieImageRecommendation.DoesNotExist:
        print(f"[WARN] No recommendations found for movie_id {movie_id}")
        return []