from django.core.management.base import BaseCommand
from recommender.models import MovieImageEmbedding, MovieImageRecommendation
from annoy import AnnoyIndex
from tqdm import tqdm
import numpy as np

class Command(BaseCommand):
    help = "Precompute and store image-based movie recommendations using Annoy"

    def add_arguments(self, parser):
        parser.add_argument(
            '--top-k',
            type=int,
            default=5,
            help='Number of similar movies to store per movie (required for Annoy)'
        )
        parser.add_argument(
            '--num-trees',
            type=int,
            default=50,
            help='Number of trees for Annoy index (higher = more accurate, slower to build)'
        )

    def handle(self, *args, **options):
        top_k = options['top_k']
        num_trees = options['num_trees']
        embeddings = []
        ids = []
        movie_lookup = {}

        for emb in MovieImageEmbedding.objects.select_related("movie"):
            vec = emb.get_embedding()
            embeddings.append(vec)
            ids.append(emb.movie.movie_id)
            movie_lookup[emb.movie.movie_id] = emb.movie

        if not embeddings:
            tqdm.write("[WARN] No embeddings found")
            return

        embeddings = np.vstack(embeddings).astype("float32")
        dim = embeddings.shape[1]
        index = AnnoyIndex(dim, 'angular')  # 'angular' ≈ cosine similarity

        tqdm.write(f"[INFO] Building Annoy index with {num_trees} trees...")
        for i, vec in enumerate(embeddings):
            index.add_item(i, vec)

        index.build(num_trees)

        updated = 0
        skipped = 0

        progress = tqdm(enumerate(ids), total=len(ids), desc="Generating recommendations", unit="movie")

        for idx, movie_id in progress:
            try:
                movie = movie_lookup[movie_id]
                progress.set_postfix_str(movie.title[:40]) 
                should_skip = False

                try:
                    existing = MovieImageRecommendation.objects.get(movie=movie)
                    if len(existing.recommended_movies) >= top_k:
                        skipped += 1
                        should_skip = True
                except MovieImageRecommendation.DoesNotExist:
                    pass

                if should_skip:
                    continue

                query_k = top_k + 1
                nearest_indices = index.get_nns_by_item(idx, query_k, search_k=-1)

                top_similar = [
                    int(ids[i])
                    for i in nearest_indices
                    if ids[i] != movie_id
                ]

                MovieImageRecommendation.objects.update_or_create(
                    movie=movie,
                    defaults={"recommended_movies": top_similar}
                )
                updated += 1

            except Exception as e:
                tqdm.write(f"[ERROR] Failed for movie {movie_id}: {e}")

        tqdm.write(f"[DONE] Recommendations complete. Updated or created: {updated}, Skipped: {skipped}")
