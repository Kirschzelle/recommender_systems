from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = "Runs all preprocessing steps: embeddings and recommendations"

    def add_arguments(self, parser):
        parser.add_argument(
            '--fetch-posters',
            action='store_true',
            help='Attempt to fetch posters during movie import'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting full preprocessing pipeline..."))

        try:
            self.stdout.write(self.style.NOTICE("Importing movies (with --clear)..."))
            call_command("import_movies", clear=True, fetch_posters=options['fetch_posters'])
            self.stdout.write(self.style.SUCCESS("Movies imported."))

            self.stdout.write(self.style.NOTICE("Computing image embeddings."))
            call_command("compute_image_embeddings")
            self.stdout.write(self.style.SUCCESS("Embeddings complete."))

            self.stdout.write(self.style.NOTICE("Computing image-based recommendations."))
            call_command("build_image_recommendations", top_k=5, num_trees=1000)
            self.stdout.write(self.style.SUCCESS("Recommendations complete."))

            self.stdout.write(self.style.SUCCESS("Preprocessing finished."))

        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"[FAIL] Preprocessing failed: {e}"))