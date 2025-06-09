import os
import json
from django.core.files import File
from recommender.models import Movie

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
    genres = ", ".join(movie_data.get("genres", [])).strip()
    overview = tmdb_data.get("overview", "")
    directors = ", ".join(imdb_data.get("directors", [])).strip()

    raw_actors = imdb_data.get("actors", [])
    if raw_actors:
        raw_actors_str = raw_actors[0]
        actors = raw_actors_str.replace("Stars:", "").split("|")[0].strip()
    
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
        print(f"Error in movie {movie_id, title}")
        
    poster_path = os.path.join(poster_dir, f"{movie_id}.jpg")
    if os.path.exists(poster_path) and not movie.poster:
        with open(poster_path, 'rb') as poster_file:
            movie.poster.save(f"{movie_id}.jpg", File(poster_file), save=False)

    movie.save()
    print(f"Imported: {title} ({release_year}) ({movie_id}) ({directors}) ({genres})")