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
    context = {
        "movie": movie_object
    }
    return render(request, "detailed_view.html", context)