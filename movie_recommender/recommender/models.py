from django.db import models
import numpy as np

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

class MovieImageEmbedding(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, related_name="image_embedding")
    embedding = models.BinaryField()

    def set_embedding(self, vector):
        self.embedding = np.asarray(vector, dtype=np.float32).tobytes()

    def get_embedding(self):
        return np.frombuffer(self.embedding, dtype=np.float32)
    
class MovieImageRecommendation(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, related_name="image_recommendations")
    recommended_movies = models.JSONField()

class MovieGenreRecommendation(models.Model):
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE, related_name="genre_recommendations")
    recommended_movies = models.JSONField()

class MovieCollaboratorRecommendation(models.Model):
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE, related_name="collaboratour_recommendations")
    recommended_movies = models.JSONField()