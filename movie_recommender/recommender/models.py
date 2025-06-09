from django.db import models

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=50)
    
class Director(models.Model):
    name = models.CharField(max_length=100)
    
class Actor(models.Model):
    name = models.CharField(max_length=100)    


class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    release_year = models.IntegerField()
    poster = models.ImageField(upload_to='posters/', blank=False)
    genres = models.ManyToManyField(Genre, blank=False)
    directors = models.ManyToManyField(Director, blank=False)
    actors = models.ManyToManyField(Actor, blank=False)