import os
import numpy as np
import torch
import faiss
from PIL import Image
from django.conf import settings
from recommender.models import Movie
from torchvision import transforms
from torchvision.models import efficientnet_b0

# Globals
MODEL = efficientnet_b0(pretrained=True)
MODEL.classifier = torch.nn.Identity()
MODEL.eval()

TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

EMBEDDING_DIR = os.path.join(settings.BASE_DIR, 'datasets', 'images')
EMBEDDINGS_PATH = os.path.join(EMBEDDING_DIR, 'movie_embeddings.npy')
IDS_PATH = os.path.join(EMBEDDING_DIR, 'movie_ids.npy')
INDEX_PATH = os.path.join(EMBEDDING_DIR, 'movie_index.faiss')

def get_image_based_recommendation(movie_id, recommendation_amount):
    try:
        index = faiss.read_index(INDEX_PATH)
        embeddings = np.load(EMBEDDINGS_PATH)
        movie_ids = np.load(IDS_PATH)

        idx = np.where(movie_ids == movie_id)[0][0]
        query_embedding = embeddings[idx].reshape(1, -1)
        _, indices = index.search(query_embedding, recommendation_amount + 1)

        similar_ids = [int(movie_ids[i]) for i in indices[0] if movie_ids[i] != movie_id]
        return similar_ids[:recommendation_amount]
    except Exception as e:
        print(f"[ERROR] Recommendation failed: {e}")
        return []

def compute_embeddings():
    os.makedirs(EMBEDDING_DIR, exist_ok=True)

    embeddings = []
    ids = []

    movies = Movie.objects.all()
    if not movies.exists():
        print("[WARN] No movies found in the database.")
        return

    for movie in movies:
        try:
            path = os.path.join(settings.MEDIA_ROOT, str(movie.poster))
            if not os.path.exists(path):
                print(f"[WARN] Poster not found for {movie.title}: {path}")
                continue

            img = Image.open(path).convert("RGB")
            tensor = TRANSFORM(img).unsqueeze(0)
            with torch.no_grad():
                embedding = MODEL(tensor).squeeze(0).numpy()
            embeddings.append(embedding)
            ids.append(movie.movie_id)

        except Exception as e:
            print(f"[ERROR] Failed to embed {movie.title}: {e}")

    if not embeddings:
        print("[ERROR] No embeddings were computed, check that posters exist and are accessible.")
        return

    np.save(EMBEDDINGS_PATH, np.vstack(embeddings))
    np.save(IDS_PATH, np.array(ids))
    print(f"[INFO] Saved {len(ids)} embeddings to {EMBEDDING_DIR}")

def build_similarity_index():
    embeddings = np.load(EMBEDDINGS_PATH)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)
    print(f"[INFO] Index built and saved to {INDEX_PATH}")


def rebuild_image_similarity(force=False):
    """
    Only compute & build if data is missing or `force=True`.
    """
    os.makedirs(EMBEDDING_DIR, exist_ok=True)

    # Only compute if not already there
    if force or not os.path.exists(EMBEDDINGS_PATH):
        print("[INFO] No embeddings found, computing now...")
        compute_embeddings()
    else:
        print("[INFO] Embeddings file already exists. Skipping compute.")

    # Only build if embeddings exist
    if os.path.exists(EMBEDDINGS_PATH):
        print("[INFO] Building similarity index...")
        build_similarity_index()
    else:
        print("[WARN] Skipping index build, embeddings not found.")