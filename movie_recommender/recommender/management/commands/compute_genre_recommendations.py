from django.core.management.base import BaseCommand
from annoy import AnnoyIndex
import numpy as np
from tqdm import tqdm

from recommender.models import Movie, MovieGenreRecommendation

class Command(BaseCommand):
    help = "Generate movie recommendations based on genre similarity using Annoy"

    def add_arguments(self, parser):
        parser.add_argument("--top-k", type=int, default=10)

    def handle(self, *args, **kwargs):
        tqdm.write("[INFO] Starting Genre recommendation generation...")

        # Extract all genres
        movies = list(Movie.objects.all())
        if not movies:
            tqdm.write("[WARN] No movies found in database.")
            return

        movie_id_map = {i: movie.movie_id for i, movie in enumerate(movies)}

        # Extract all genres
        tqdm.write(f"[INFO] Extracting Genres from {len(movies)} movies...")
        all_genres = set()
        for movie in movies:
            genres = [g.strip().lower() for g in movie.genres.split(',') if g.strip()]
            all_genres.update(genres)

        genre_list = sorted(all_genres)
        genre_to_idx = {genre: idx for idx, genre in enumerate(genre_list)}
        dim = len(genre_list)
        tqdm.write(f"[INFO] Total unique Genres: {dim}")

        # Build movie vectors
        def movie_to_vector(movie):
            vec = np.zeros(dim, dtype=np.float32)
            for genre in movie.genres.split(','):
                genre = genre.strip().lower()
                idx = genre_to_idx.get(genre)
                if idx is not None:
                    vec[idx] = 1.0
            return vec

        tqdm.write("[INFO] Vectorizing movies...")
        movie_vectors = np.array([movie_to_vector(movie) for movie in tqdm(movies)])

        # Build Annoy index
        tqdm.write("[INFO] Building Annoy index...")
        index = AnnoyIndex(dim, 'angular')
        for i, vec in enumerate(movie_vectors):
            index.add_item(i, vec.tolist())

        index.build(10)
        tqdm.write("[INFO] Annoy index built successfully.")

        # Save recommendations
        tqdm.write("[INFO] Saving Genre-based recommendations to database...")
        MovieGenreRecommendation.objects.all().delete()

        top_k = kwargs["top_k"]
        recommendations = []
        for i, movie in enumerate(movies):
            neighbor_ids = index.get_nns_by_item(i, top_k+1)
            recommended_ids = [movie_id_map[nid] for nid in neighbor_ids if nid != i][:top_k]

            recommendations.append(
                MovieGenreRecommendation(
                    movie=movie,
                    recommended_movies=recommended_ids
                )
            )

            if i % 100 == 0:
                tqdm.write(f"[INFO] Processed {i}/{len(movies)} movies")

        MovieGenreRecommendation.objects.bulk_create(recommendations)
        tqdm.write("[INFO] Genre-based recommendations saved successfully.")