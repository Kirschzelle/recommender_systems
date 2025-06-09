from django.shortcuts import render
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