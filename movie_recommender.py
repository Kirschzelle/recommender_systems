from data import Data
from strategies.recommendation_genres import recommendation_genres
from strategies.recommendation_collaborators import recommendation_collaborators


def get_recommendation(movie_id, recommendation_amount, function_id):
    """
    Dispatches a movie recommendation request to one of several recommendation strategies.

    Parameters:
    movie_id (int): The MovieLens ID of the reference movie.
    recommendation_amount (int): The number of movie recommendations to return.
    function_id (int): The ID representing one of the implemented recommendation strategies (1-5).

    Returns:
    list: A list of recommended movie IDs based on the selected recommendation strategy.

    Notes:
    
    This function acts as an interface between the frontend and backend.
    Each function_id corresponds to a distinct recommendation algorithm, implemented separately.
    """
    
    if recommendation_amount != 5:
        print(f"Expected 5 recommendations. You requested {recommendation_amount}.  Are you sure you a different number of recommendations?")

    data = Data()

    match function_id:
        case 1:
            return recommendation_placeholder(movie_id, recommendation_amount)
        case 2:
            return recommendation_genres(movie_id, recommendation_amount, data)
        case 3:
            return recommendation_collaborators(movie_id, recommendation_amount, data)
        case 4:
            return recommendation_placeholder(movie_id, recommendation_amount)
        case 5:
            return recommendation_placeholder(movie_id, recommendation_amount)
        case _:
            return recommendation_placeholder(movie_id, recommendation_amount)
    
def recommendation_placeholder(movie_id, recommendation_amount): 
    """
    Placeholder recommendation function used during development.

    Parameters:
    movie_id (int): The MovieLens ID of the reference movie.
    recommendation_amount (int): The number of movie recommendations to return.

    Returns:
    list: A list of recommendation_amount elements, each being the input movie_id.

    Notes:
    
    This function is a temporary stand-in to allow the frontend to function without the finalized backend logic.
    It simply returns the input movie ID multiple times and should be replaced with actual recommendation logic.
    """
    
    recommendations = [movie_id for _ in range(recommendation_amount)]
    return recommendations