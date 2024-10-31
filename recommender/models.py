from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=255)
    overview = models.TextField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    genres = models.TextField(null=True, blank=True)  # Store as a comma-separated string
    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)

class Rating(models.Model):
    userId = models.IntegerField(null=True, blank=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField(null=True, blank=True)

class Keyword(models.Model):
    movie = models.ForeignKey(Movie, related_name='keywords', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

class Credit(models.Model):
    movie = models.ForeignKey(Movie, related_name='credits', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)  # e.g., Actor or Director