from algorithms.movie_recommender import get_recommendation
from django.shortcuts import render, get_object_or_404
from .models import Movie

# Create your views here.
def home_view(request):
    query = request.GET.get("q")
    movie_objects = None
    if query:
        movie_objects = Movie.objects.filter(title__icontains = query)
    context = {
        "query": query,
        "movie_objects": movie_objects
    }
    return render(request, "home.html", context)

def detailed_movie_view(request, movie_id):
    movie_object = get_object_or_404(Movie, movie_id = movie_id)
    recommendation_amount = 5
    
    all_recommendations = {}
    method_names = {
        1: "Random",
        2: "TBA2",
        3: "TBA3",
        4: "TBA4",
        5: "TBA5",
    }
    
    for function_id in range(1, 6):
        recommended_ids = get_recommendation(movie_id, recommendation_amount, function_id)
        recommended_movies = Movie.objects.filter(movie_id__in = recommended_ids)
        all_recommendations[f"{method_names[function_id]}"] = recommended_movies
    
    context = {
        "movie": movie_object,
        "all_recommendations": all_recommendations
    }
    return render(request, "detailed_view.html", context)