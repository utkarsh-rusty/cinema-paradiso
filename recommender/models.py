from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    release_date = models.IntegerField(default=0)
    rating = models.FloatField()
    overview = models.TextField()
    runtime = models.TextField(default="null")
    num_votes = models.IntegerField(default=0)

    def __str__(self):
        return self.title