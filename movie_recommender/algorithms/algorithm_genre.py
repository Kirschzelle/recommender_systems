from recommender.models import MovieGenreRecommendation


def get_genre_recommendations(movie_id, num_recommendations):
    try:
        recommendations = MovieGenreRecommendation.objects.get(movie_id=movie_id)
        return recommendations.recommended_movies[:num_recommendations]
    except MovieGenreRecommendation.DoesNotExist:
        print(f"[WARN] No recommendations found for movie_id {movie_id}")
        return []
        