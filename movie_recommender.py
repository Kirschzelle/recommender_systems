import time

import data

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
    
    match function_id:
        case 1:
            return recommendation_placeholder(movie_id, recommendation_amount)
        case 2:
            return recommendation_genre(movie_id, recommendation_amount)
        case 3:
            return recommendation_collaborators(movie_id, recommendation_amount)
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

def recommendation_genre(movie_id, recommendation_amount):
    if movie_id not in data.movies_df['movieId'].values:
        raise Exception(f"Movie ID {movie_id} not found.")

    movie_index = data.movies_df[data.movies_df['movieId'] == movie_id].index[0]

    similarity_scores = list(enumerate(data.genre_cosine_similarity_matrix[movie_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommendations_ids = []
    count = 0
    for idx, score in similarity_scores:
        if idx == movie_index:
            continue
        recommendations_ids.append(int(data.movies_df.iloc[idx]['movieId']))
        count += 1
        if count >= recommendation_amount:
            break
    return recommendations_ids

def recommendation_collaborators(movie_id, recommendation_amount):
    if movie_id not in data.movies_with_people_df['movieId'].values:
        raise Exception(f"Movie ID {movie_id} not found.")

    movie_index = data.movies_with_people_df[data.movies_with_people_df['movieId'] == movie_id].index[0]

    similarity_scores = list(enumerate(data.collaborators_cosine_similarity_matrix[movie_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommendations_ids = []
    count = 0
    for idx, score in similarity_scores:
        if idx == movie_index:
            continue
        recommendations_ids.append(int(data.movies_with_people_df.iloc[idx]['movieId']))
        count += 1
        if count >= recommendation_amount:
            break
    return recommendations_ids

def print_time(elapsed_time):
    hours, remaining = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remaining, 60)
    print(f"Time elapsed: {hours:02}:{minutes:02}:{seconds:02}")

if __name__ == "__main__":
    data.precompute()

    while(True):
        i = int(input("Please enter movie ID: "))

        print("Genre:")
        start = time.time()
        print(recommendation_genre(i, 10))
        end = time.time()

        print_time(end - start)

        print("\nCollaborators:")
        start = time.time()
        print(recommendation_collaborators(i, 10))
        end = time.time()

        print_time(end - start)