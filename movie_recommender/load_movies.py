import os
import json
import re
import urllib
from django.core.files import File
from urllib.request import urlopen
from django.core.files.base import ContentFile
from recommender.models import Movie

def get_poster_url(imdb_link):
    headers = {'User-Agent': 'Mozilla/5.0'}

    req = urllib.request.Request(imdb_link, headers=headers)
    with urllib.request.urlopen(req) as response:
        html = response.read().decode("utf-8")

    match = re.search(r'<meta property="og:image" content="(https://m\.media-amazon\.com/[^"]+)"', html)
    if match:
        return match.group(1)
    return None

def get_genres():
    genres_raw = movie_data.get("genres", [])
    if isinstance(genres_raw, str):
        genres = genres_raw
    elif isinstance(genres_raw, list):
        genres = ", ".join(genres_raw)
    else:
        genres = ""
    return genres

def get_directors():
    directors_raw = imdb_data.get("directors", [])
    if isinstance(directors_raw, str):
        directors = directors_raw
    elif isinstance(directors_raw, list):
        directors = ", ".join(directors_raw)
    else:
        directors = ""
    return directors
    
def get_actors():
    raw_actors = imdb_data.get("actors", [])
    if raw_actors:
        raw_actors_str = raw_actors[0]
        return raw_actors_str.replace("Stars:", "").split("|")[0].strip()


Movie.objects.all().delete()
print("Deleted old databse entries.")
base_dir = "datasets"
info_dir = os.path.join(base_dir, "information")
poster_dir = os.path.join(base_dir, "posters")

for filename in os.listdir(info_dir):
    if not filename.endswith(".json"):
        continue
    
    file_path = os.path.join(info_dir, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Failed to parse {filename}")
            continue

    movie_data = data.get("movielens", {})
    tmdb_data = data.get("tmdb", {})
    imdb_data = data.get("imdb", {})
    
    movie_id = movie_data.get("movieId")
    if not movie_id:
        continue

    title = movie_data.get("title", "")
    release_year = int(movie_data.get("releaseYear", 0) or 0)
    genres = get_genres()
    overview = tmdb_data.get("overview", "")
    directors = get_directors()
    actors = get_actors()
    
    try:    
        movie, created = Movie.objects.get_or_create(
            movie_id = movie_id,
            defaults = {
                "title": title,
                "overview": overview,
                "release_year": release_year,
                "actors": actors,
                "genres": genres,
                "directors": directors
            }
        )
    except:
        print(f"Error creating movie {movie_id, title}")
        
    poster_path = os.path.join(poster_dir, f"{movie_id}.jpg")
    fallback_path = os.path.join(poster_dir, "0.png")
    if os.path.exists(poster_path):
        with open(poster_path, 'rb') as poster_file:
            movie.poster.save(f"{movie_id}.jpg", File(poster_file), save=False)
    else:
        """print(f"No local poster found, importing '{title}' from web!")
        imdb_link = imdb_data.get("imdbLink")
        poster = get_poster_url(imdb_link)
        if poster:
            try:
                with urlopen(poster) as response:
                    image_data = response.read()
                    movie.poster.save(f"{movie_id}.jpg", ContentFile(image_data), save=False)
            except Exception as e:
                print(f"Failed to download poster for {movie_id}: {e}")"""
        with open(fallback_path, 'rb') as poster_file:
            movie.poster.save(f"0_{movie_id}.jpg", File(poster_file), save=False)
            
    movie.save()
    print(f"Imported: {title} ({release_year}) ({movie_id}) ({directors}) ({genres})")
    
print("Imported all movies!")