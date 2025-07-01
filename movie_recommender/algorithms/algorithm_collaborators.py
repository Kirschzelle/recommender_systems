from recommender.models import MovieCollaboratorRecommendation


def get_collaborators_recommendations(movie_id, num_recommendations):
    try:
        recommendations = MovieCollaboratorRecommendation.objects.get(movie_id=movie_id)
        return recommendations.recommended_movies[:num_recommendations]
    except MovieCollaboratorRecommendation.DoesNotExist:
        print(f"[WARN] No recommendations found for movie_id {movie_id}")
        return []
