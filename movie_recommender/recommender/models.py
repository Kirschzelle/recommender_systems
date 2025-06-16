from django.db import models

# Create your models here.
class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    release_year = models.IntegerField()
    actors = models.CharField(max_length=500, blank=False)
    genres = models.CharField(max_length=500, blank=False)
    directors = models.CharField(max_length=500, blank=False)
    poster = models.ImageField(upload_to='posters/', blank=False)