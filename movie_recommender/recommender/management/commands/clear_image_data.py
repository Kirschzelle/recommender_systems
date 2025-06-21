from django.core.management.base import BaseCommand
from recommender.models import MovieImageEmbedding, MovieImageRecommendation

class Command(BaseCommand):
    help = "Clear all stored image embeddings and recommendations"

    def handle(self, *args, **kwargs):
        confirm = input("This will delete all image embeddings and recommendations. Continue? (y/N): ")
        if confirm.lower() != "y":
            self.stdout.write(self.style.WARNING("Aborted."))
            return

        num_embeddings = MovieImageEmbedding.objects.count()
        num_recommendations = MovieImageRecommendation.objects.count()

        MovieImageEmbedding.objects.all().delete()
        MovieImageRecommendation.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(
            f"Cleared {num_embeddings} embeddings and {num_recommendations} recommendations."
        ))
