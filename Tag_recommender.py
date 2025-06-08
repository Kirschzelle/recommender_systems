import pandas as pd
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def load_tag_matrix(data_dir):
    '''this function loads the data from the data directory. all datasets should be located in the data directory.
      Input:  
      data_dir=Path("/Users/minafam/Documents/Project/recommender_systems/data/ml-20m")

      Returns:
            pandas.DataFrame: A matrix where rows are movieIds and columns are tagIds,
            and values are relevance scores.     
      '''
    
    # Check if data_dir is a valid Path object
    if not isinstance(data_dir, Path):
        raise TypeError("data_dir must be a Path object")

    # Check if data directory exists
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found at: {data_dir}")

    # Check if genome-scores.csv exists
    genome_scores_path = data_dir / "genome-scores.csv"
    if not genome_scores_path.exists():
        raise FileNotFoundError(f"genome-scores.csv not found in {data_dir}")

    try:
        #load the data for genome-scores.csv which is the tag data
        tag_df = pd.read_csv(genome_scores_path)
        
        # Create tag matrix
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
        print("Computing similarity matrix for all movies...")
        self.similarity_matrix = cosine_similarity(self.tag_matrix)
        self.movie_ids = self.tag_matrix.index.tolist()
        print("Recommender system ready!")

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
            # Find the index of the movie in our matrix
            movie_idx = self.movie_ids.index(movie_id)
            
            # Get similarities for this movie (already computed)
            similarities = self.similarity_matrix[movie_idx]
            
            # Get indices of top N most similar movies (excluding the input movie itself)
            top_indices = np.argsort(similarities)[::-1][1:recommendation_amount+1]
            
            # Convert indices back to movie IDs
            recommendations = [self.movie_ids[idx] for idx in top_indices]
            
            return recommendations
            
        except ValueError:
            raise ValueError(f"Movie ID {movie_id} not found in the dataset")


if __name__ == "__main__":
    # Initialize the recommender system (this will precompute all similarities)
    project_path = Path.cwd()
    data_dir = project_path / "data" / "ml-20m"
    
    # Create recommender instance (this will precompute similarities)
    recommender = TagRecommender(data_dir)
    
    # Example usage
    movie_id = 5
    recommendation_amount = 5
    
    # Get recommendations (this will be fast since similarities are precomputed)
    recommendations = recommender.get_recommendations(movie_id, recommendation_amount)
    print(f"\nTop {recommendation_amount} recommendations for movie {movie_id}:")
    print(recommendations)


    movie_id=6
    recommendation_amount=5
    recommendations = recommender.get_recommendations(movie_id, recommendation_amount)
    print(f"\nTop {recommendation_amount} recommendations for movie {movie_id}:")
    print(recommendations)



    