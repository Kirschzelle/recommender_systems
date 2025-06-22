def recommendation_genres(movie_id, recommendation_amount, data):
    if movie_id not in data.additional_data_df['movieId'].values:
        raise Exception(f"Movie ID {movie_id} not found.")

    movie_index = data.additional_data_df[data.additional_data_df['movieId'] == movie_id].index[0]

    similarity_scores = list(enumerate(data.genre_cosine_similarity_matrix[movie_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommendations_ids = []
    count = 0
    for idx, _ in similarity_scores:
        if idx == movie_index:
            continue
        recommendations_ids.append(int(data.additional_data_df.iloc[idx]['movieId']))
        count += 1
        if count >= recommendation_amount:
            break
    return recommendations_ids
