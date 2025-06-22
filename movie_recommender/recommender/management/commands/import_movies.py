import os
import json
from django.core.management.base import BaseCommand
from django.core.files import File
from recommender.models import Movie
from duckduckgo_search import DDGS
from PIL import Image
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

class Command(BaseCommand):
    help = "Import movie data and posters from JSON files"

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-dir',
            type=str,
            default='datasets',
            help='Base directory containing the information and posters folders'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing Movie entries before import'
        )
        parser.add_argument(
            '--fetch-posters',
            action='store_true',
            help='Attempt to fetch missing posters from TMDB or DuckDuckGo'
        )

    def handle(self, *args, **options):
        self.missing_movies = []
        base_dir = options['base_dir']
        info_dir = os.path.join(base_dir, "information")
        poster_dir = os.path.join(base_dir, "posters")
        fallback_path = os.path.join(poster_dir, "0.png")

        if options['clear']:
            confirm = input("Are you sure you want to delete all existing movies? Type 'yes' to continue: ")
            if confirm.lower() == 'yes':
                Movie.objects.all().delete()
                self.stdout.write(self.style.WARNING("Deleted all existing movies."))
            else:
                self.stdout.write(self.style.WARNING("Aborted movie deletion."))

        files = [f for f in os.listdir(info_dir) if f.endswith(".json")]
        for filename in tqdm(files, desc="Importing movies", unit="file"):
            file_path = os.path.join(info_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                self.stderr.write(f"[ERROR] Failed to parse {filename}")
                continue

            movie_data = data.get("movielens", {})
            tmdb_data = data.get("tmdb", {})
            imdb_data = data.get("imdb", {})

            movie_id = movie_data.get("movieId")
            if not movie_id:
                continue

            title = movie_data.get("title", "")
            release_year = int(movie_data.get("releaseYear", 0) or 0)
            genres = self.get_list(movie_data.get("genres"))
            overview = tmdb_data.get("overview", "")
            directors = self.get_list(imdb_data.get("directors"))
            actors = self.parse_actors(imdb_data.get("actors"))

            try:
                movie, _ = Movie.objects.get_or_create(
                    movie_id=movie_id,
                    defaults={
                        "title": title,
                        "overview": overview,
                        "release_year": release_year,
                        "actors": actors,
                        "genres": genres,
                        "directors": directors,
                    }
                )
            except Exception as e:
                self.stderr.write(f"[ERROR] Failed to create movie {movie_id}: {e}")
                continue

            poster_path = os.path.join(poster_dir, f"{movie_id}.jpg")
            if os.path.exists(poster_path):
                with open(poster_path, 'rb') as f:
                    movie.poster.save(f"{movie_id}.jpg", File(f), save=False)
            else:
                self.missing_movies.append((movie.pk, title))

            movie.save()
            self.stdout.write(f"[OK] Imported: {title} ({movie_id})")

        if self.missing_movies:
            if options['fetch_posters']:
                print(f"[INFO] Fetching {len(self.missing_movies)} web posters in background threads...")
                with ThreadPoolExecutor(max_workers=8) as executor:
                    futures = [
                        executor.submit(fetch_and_save_poster, movie_id, title, fallback_path)
                        for movie_id, title in self.missing_movies
                    ]
                    for future in tqdm(futures, desc="Downloading posters", unit="img"):
                        try:
                            future.result()
                        except Exception as e:
                            print(f"[ERROR] Threaded download failed: {e}")
            else:
                for movie_id, _ in self.missing_movies:
                    movie = Movie.objects.get(pk=movie_id)
                    with open(fallback_path, 'rb') as f:
                        movie.poster.save(f"0_{movie_id}.png", File(f), save=False)

        self.stdout.write(self.style.SUCCESS("🎉 Import complete."))

    def get_list(self, value):
        if isinstance(value, list):
            return ", ".join(value)
        elif isinstance(value, str):
            return value
        return ""

    def parse_actors(self, actors_field):
        if not actors_field:
            return ""
        actors = actors_field[0] if isinstance(actors_field, list) else actors_field
        return actors.replace("Stars:", "").split("|")[0].strip()
    

def fetch_tmdb_poster(title, api_key):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": api_key, "query": title}
    resp = requests.get(url, params=params)
    data = resp.json()
    
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None
    
def fetch_online_poster(movie_title):
    from urllib.parse import quote

    try:
        with DDGS() as ddgs:
            queries = [f"{movie_title} movie poster", movie_title]

            for query in queries:
                try:
                    results = ddgs.images(query, max_results=1, safesearch="off")
                    result = results[0] if results else None

                    if result and 'image' in result:
                        image_url = result['image']
                        response = requests.get(image_url, timeout=10)
                        response.raise_for_status()
                        image = Image.open(BytesIO(response.content)).convert("RGB")
                        image = image.resize((500, 750))
                        return image
                    else:
                        print(f"[DEBUG] No image found for query: '{query}'")
                except Exception as inner_e:
                    print(f"[ERROR] Query failed for '{query}': {inner_e}")
                    continue

    except Exception as e:
        print(f"[WARN] Failed DuckDuckGo session for '{movie_title}': {e}")

    return None
    
def fetch_and_save_poster(movie_id, title, fallback_path):
    import time
    from recommender.models import Movie

    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    movie = Movie.objects.get(pk=movie_id)

    poster_url = fetch_tmdb_poster(title, TMDB_API_KEY)
    if poster_url:
        try:
            response = requests.get(poster_url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGB")
            image = image.resize((500, 750))
            buffer = BytesIO()
            image.save(buffer, format='JPEG')
            movie.poster.save(f"tmdb_{movie_id}.jpg", ContentFile(buffer.getvalue()), save=True)
            print(f"[THREAD] TMDB poster fetched for {title}")
            return
        except Exception as e:
            print(f"[WARN] TMDB fetch failed for '{title}': {e}")

    time.sleep(2)
    image = fetch_online_poster(title)
    if image:
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        movie.poster.save(f"web_{movie_id}.jpg", ContentFile(buffer.getvalue()), save=True)
        print(f"[THREAD] DuckDuckGo poster fetched for {title}")
    else:
        with open(fallback_path, 'rb') as f:
            movie.poster.save(f"0_{movie_id}.png", File(f), save=False)
        print(f"[THREAD] Using fallback for '{title}'")
