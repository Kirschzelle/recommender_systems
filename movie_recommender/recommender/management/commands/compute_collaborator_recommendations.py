from django.core.management.base import BaseCommand
import numpy as np
import faiss
from tqdm import tqdm

from recommender.models import Movie, MovieCollaboratorRecommendation


class Command(BaseCommand):
    help = "Generate movie recommendations based on collaborators similarity using FAISS"

    def add_arguments(self, parser):
        parser.add_argument("--top-k", type=int, default=10)

    def handle(self, *args, **kwargs):
        tqdm.write("[INFO] Starting Collaborator recommendation generation...")

        movies = list(Movie.objects.only("movie_id", "directors", "actors"))
        if not movies:
            tqdm.write("[WARN] No movies found in database.")
            return

        movie_ids = [movie.movie_id for movie in movies]

        # Extract the directors and five main actors
        def get_collaborators(movie):
            directors = [d.strip().lower() for d in movie.directors.split(',') if d.strip()]
            actors = [a.strip().lower() for a in movie.actors.split(',') if a.strip()][:5]
            return directors + actors

        tqdm.write(f"[INFO] Extracting Collaborators from {len(movies)} movies...")
        all_collaborators = set()
        for movie in movies:
            all_collaborators.update(get_collaborators(movie))

        collaborator_list = sorted(all_collaborators)
        collaborator_to_idx = {collaborator: idx for idx, collaborator in enumerate(collaborator_list)}
        dim = len(collaborator_list)
        tqdm.write(f"[INFO] Total unique Collaborators: {dim}")

        # Build movie vectors
        def movie_to_vector(movie):
            vec = np.zeros(dim, dtype=np.float32)
            for collaborator in get_collaborators(movie):
                idx = collaborator_to_idx.get(collaborator)
                if idx is not None:
                    vec[idx] = 1.0
            return vec

        tqdm.write("[INFO] Vectorizing movies...")
        movie_vectors = np.array([movie_to_vector(movie) for movie in movies], dtype=np.float32)
        faiss.normalize_L2(movie_vectors)

        # Build FAISS index
        tqdm.write("[INFO] Building FAISS index...")
        index = faiss.IndexFlatIP(dim)
        index.add(movie_vectors)
        tqdm.write("[INFO] FAISS index built successfully.")

        top_k = kwargs["top_k"]

        tqdm.write("[INFO] Searching for nearest neighbors...")
        D, I = index.search(movie_vectors, top_k + 1)  # includes self

        # Save recommendations
        tqdm.write("[INFO] Delete old recommendations...")
        MovieCollaboratorRecommendation.objects.all().delete()

        tqdm.write("[INFO] Generating recommendations for all movies...")

        recommendations_data = []
        for i in range(len(movies)):
            neighbors = I[i]
            recommended_movie_ids = [movie_ids[nid] for nid in neighbors if nid != i][:top_k]
            recommendations_data.append((movies[i], recommended_movie_ids))

        tqdm.write("[INFO] Creating MovieCollaboratorRecommendation instances for bulk_create...")
        recommendations_objs = [
            MovieCollaboratorRecommendation(movie=movie, recommended_movies=recommended_ids)
            for movie, recommended_ids in recommendations_data
        ]

        tqdm.write("[INFO] Bulk creating recommendations in database...")
        MovieCollaboratorRecommendation.objects.bulk_create(recommendations_objs)

        tqdm.write(f"[INFO] Collaborator-based recommendations saved successfully.")