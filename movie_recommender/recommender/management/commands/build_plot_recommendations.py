from django.core.management.base import BaseCommand
from recommender.models import Movie, MovieLdaEmbedding, MoviePlotRecommendation
from algorithms.algorithm_plot_topic import LdaData
from tqdm import tqdm
import numpy as np
import os

class Command(BaseCommand):
    help = "Precompute and store plot-based movie recommendations using LDA"

    def add_arguments(self, parser):
        parser.add_argument(
            '--top-k',
            type=int,
            default=5,
            help='Number of similar movies to store per movie'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing plot recommendations before computing new ones'
        )

    def handle(self, *args, **options):
        top_k = options['top_k']
        clear_existing = options['clear']
        
        if clear_existing:
            self.stdout.write("Clearing existing plot recommendations...")
            MoviePlotRecommendation.objects.all().delete()
            MovieLdaEmbedding.objects.all().delete()
        
        # Get the data directory
        this_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        data_dir = os.path.abspath(os.path.join(this_dir, "datasets", "information"))
        
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f"Data directory not found: {data_dir}"))
            return
        
        # Initialize LDA system (this will show progress bars)
        self.stdout.write("Initializing LDA recommendation system...")
        lda_data = LdaData(data_dir)
        
        # Get all movies that have LDA data
        movie_ids_with_lda = set(lda_data.movie_ids)
        movies = Movie.objects.filter(movie_id__in=movie_ids_with_lda)
        
        if not movies.exists():
            self.stdout.write(self.style.WARNING("No movies found with LDA data"))
            return
        
        self.stdout.write(f"Computing recommendations for {movies.count()} movies...")
        
        updated = 0
        skipped = 0
        
        progress = tqdm(movies, desc="Generating plot recommendations", unit="movie")
        
        for movie in progress:
            try:
                progress.set_postfix_str(movie.title[:40])
                
                # Check if we already have recommendations for this movie
                try:
                    existing = MoviePlotRecommendation.objects.get(movie=movie)
                    if len(existing.recommended_movies) >= top_k:
                        skipped += 1
                        continue
                except MoviePlotRecommendation.DoesNotExist:
                    pass
                
                # Get recommendations
                recommendations = lda_data.get_recommendations(movie.movie_id, top_k)
                
                # Store recommendations
                MoviePlotRecommendation.objects.update_or_create(
                    movie=movie,
                    defaults={"recommended_movies": recommendations}
                )
                updated += 1
                
            except Exception as e:
                self.stdout.write(f"[ERROR] Failed for movie {movie.movie_id}: {e}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Plot recommendations complete. Updated: {updated}, Skipped: {skipped}"
            )
        ) 