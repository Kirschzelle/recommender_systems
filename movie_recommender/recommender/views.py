from django.shortcuts import render

# Create your views here.
def home_view(request):
    query_dict = dict(request.GET)
    query = query_dict.get("q")
    context = {
        "movie_name": query
    }
    return render(request, "home.html", context)