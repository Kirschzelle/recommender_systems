from django.apps import AppConfig

class RecommenderConfig(AppConfig):
    name = 'recommender'

    _ran_similarity = False

    def ready(self):
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver

        @receiver(post_migrate)
        def run_after_migrations(sender, **kwargs):
            if not RecommenderConfig._ran_similarity:
                RecommenderConfig._ran_similarity = True
                import threading
                from algorithms import algorithm_image
                threading.Thread(target=algorithm_image.rebuild_image_similarity).start()