import pandas as pd
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def data_load(data_dir):
    '''this function loads the data from the data directory. all datasets should be located in the data directory.
      It returns a dataframe for each dataset.
      ex. for data_dir=Path("/Users/minafam/Documents/Project/recommender_systems/data/ml-20m") '''
    
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
        
        return tag_df
        
    except pd.errors.EmptyDataError:
        raise ValueError("genome-scores.csv is empty")
    except pd.errors.ParserError:
        raise ValueError("Error parsing genome-scores.csv - file may be corrupted or in wrong format")
    except Exception as e:
        raise Exception(f"Unexpected error loading genome-scores.csv: {str(e)}")


def tag_recommender(movie_id, recommendation_amount): 
    """
    Recommend movies based on tag similarity using cosine similarity between movie tag vectors.

    Parameters:
    movie_id (int): The MovieLens ID of the reference movie
    recommendation_amount (int): The number of movie recommendations to return

    Returns:
    pandas.Index: MovieIds of the most similar movies to the input movie based on tag similarity
    """
    # Load data once when function is called
    project_path = Path.cwd()
    data_dir = project_path /"data"/"ml-20m"
    tag_df = pd.read_csv(data_dir / "genome-scores.csv")
    
    # Create tag matrix
    tag_matrix = tag_df.pivot(index="movieId",
                             columns="tagId", 
                             values="relevance").fillna(0)
    
    # Get the index of input movie
    movie_index = tag_matrix.index.get_loc(movie_id)
    
    # Calculate similarity for just the input movie compared to all others
    input_vector = tag_matrix.iloc[movie_index].values.reshape(1, -1)
    similarities = cosine_similarity(input_vector, tag_matrix)[0]
    
    # Get indices of top N most similar movies (excluding the input movie itself)
    top_movies = np.argsort(similarities)[::-1][1:recommendation_amount+1]
    
    # Return the actual movie IDs
    return tag_matrix.index[top_movies]

if __name__ == "__main__":
    movie_id=3
    recommendation_amount=5
    print(tag_recommender(movie_id,recommendation_amount))