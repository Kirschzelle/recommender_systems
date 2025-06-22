from django.core.management.base import BaseCommand
from recommender.models import Movie, MovieImageEmbedding
from PIL import Image
import os
import torch
import open_clip
import numpy as np
from django.conf import settings
from tqdm import tqdm

class Command(BaseCommand):
    help = "Compute CLIP image embeddings for movies"

    def handle(self, *args, **options):
        model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
        model.eval()

        movies = list(Movie.objects.all())

        for movie in tqdm(movies, desc="Processing movies", unit="movie"):
            try:
                if MovieImageEmbedding.objects.filter(movie=movie).exists():
                    tqdm.write(f"[SKIP] {movie.title} (embedding exists)")
                    continue

                image_path = os.path.join(settings.MEDIA_ROOT, str(movie.poster))
                if not os.path.exists(image_path):
                    tqdm.write(f"[WARN] Image not found for {movie.title}")
                    continue

                image = Image.open(image_path).convert("RGB")
                image_input = preprocess(image).unsqueeze(0)

                with torch.no_grad():
                    embedding = model.encode_image(image_input).squeeze(0).numpy()

                emb_model = MovieImageEmbedding(movie=movie)
                emb_model.set_embedding(embedding)
                emb_model.save()
                tqdm.write(f"[OK] Embedded {movie.title}")

            except Exception as e:
                tqdm.write(f"[ERROR] Failed embedding for {movie.title}: {e}")