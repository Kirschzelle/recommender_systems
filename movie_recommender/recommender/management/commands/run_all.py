from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = "Runs all preprocessing steps: embeddings and recommendations"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Starting full preprocessing pipeline..."))

        try:
            self.stdout.write(self.style.NOTICE("Computing image embeddings"))
            call_command("compute_image_embeddings")
            self.stdout.write(self.style.SUCCESS("Embeddings complete"))

            self.stdout.write(self.style.NOTICE("Computing image-based recommendations"))
            call_command("build_image_recommendations", top_k=5, num_trees=100)
            self.stdout.write(self.style.SUCCESS("Recommendations complete"))

            self.stdout.write(self.style.SUCCESS("Preprocessing finished."))

        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"[FAIL] Preprocessing failed: {e}"))
