import pandas as pd
import os
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def load_tag_matrix(data_dir):
    '''this function loads the data from the data directory. all datasets should be located in the data directory.

      Returns:
            pandas.DataFrame: A matrix where rows are movieIds and columns are tagIds,
            and values are relevance scores.     
      '''
    
    if not isinstance(data_dir,str):
        raise TypeError("data_dir must be a string")

    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found at: {data_dir}")

    genome_scores_path = os.path.join(data_dir, "genome-scores.csv")
    
    if not os.path.exists(genome_scores_path):
        raise FileNotFoundError(f"genome-scores.csv not found in {data_dir}")

    try:
        tag_df = pd.read_csv(genome_scores_path)
        tag_matrix = tag_df.pivot(index="movieId",
                                columns="tagId", 
                                values="relevance").fillna(0)
        
        return tag_matrix
        
    except pd.errors.EmptyDataError:
        raise ValueError("genome-scores.csv is empty")
    except pd.errors.ParserError:
        raise ValueError("Error parsing genome-scores.csv - file may be corrupted or in wrong format")
    except Exception as e:
        raise Exception(f"Unexpected error loading genome-scores.csv: {str(e)}")


class TagRecommender:
    def __init__(self, data_dir):
        """
        Initialize the recommender system by loading and precomputing similarities.
        
        Parameters:
        data_dir (Path): Path to the data directory containing the MovieLens dataset
        """
        self.tag_matrix = load_tag_matrix(data_dir)
        print("Computing similarity matrix by tag for all movies...")
        self.similarity_matrix = cosine_similarity(self.tag_matrix)
        self.movie_ids = self.tag_matrix.index.tolist()
        print("Recommender system based on tag is ready!")

    def get_recommendations(self, movie_id, recommendation_amount):
        """
        Get movie recommendations using precomputed tag similarities.

        Parameters:
        movie_id (int): The MovieLens ID of the reference movie
        recommendation_amount (int): The number of movie recommendations to return

        Returns:
        list: MovieIds of the most similar movies to the input movie based on tag similarity
        """
        try:
            movie_idx = self.movie_ids.index(movie_id)
            similarities = self.similarity_matrix[movie_idx]
            top_indices = np.argsort(similarities)[::-1][1:recommendation_amount+1]
            recommendations = [self.movie_ids[idx] for idx in top_indices]
            
            return recommendations
            
        except ValueError:
            raise ValueError(f"Movie ID {movie_id} not found in the dataset")
class TagData:
    _instance = None

    def __new__(cls, data_dir):
        if cls._instance is None:

            cls._instance = super().__new__(cls)
            cls._instance.recommender = TagRecommender(data_dir)
        return cls._instance
this_dir=os.path.dirname(__file__)
data_dir=os.path.abspath(os.path.join(this_dir, "..", "datasets", "ml-20m"))
tag_data = TagData(data_dir)


def get_tag_based_recommendation(movie_id, recommendation_amount):
    """
    Get movie recommendations using precomputed tag similarities.
    """

    return tag_data.recommender.get_recommendations(movie_id, recommendation_amount)
 
#for tests
if __name__ == "__main__":

    # 1) Load the movies metadata so we can map IDs → titles
    this_dir   = os.path.dirname(__file__)
    csv_path   = os.path.abspath(os.path.join(this_dir, "..", "datasets", "ml-20m", "movies.csv"))
    movies_df  = pd.read_csv(csv_path)
    id_to_title = dict(zip(movies_df["movieId"], movies_df["title"]))

    # 2) Pick a test movie by ID (or you could reverse‐lookup by title here)
    movie_id             = 5
    recommendation_amount = 5

    # 3) Get your recommendations (list of IDs)
    rec_ids = get_tag_based_recommendation(movie_id, recommendation_amount)

    # 4) Map IDs to titles
    rec_titles = [id_to_title.get(mid, f"<Unknown ID {mid}>") for mid in rec_ids]

    # 5) Print human‐friendly output
    test_title = id_to_title.get(movie_id, str(movie_id))
    print(f"\nTop {recommendation_amount} recommendations for “{test_title}”:")
    for i, title in enumerate(rec_titles, start=1):
        print(f"{i}. {title}")







    