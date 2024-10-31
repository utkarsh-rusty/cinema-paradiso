from django.contrib import admin

# Register your models here.
from .models import Movie, Rating, Keyword, Credit

admin.site.register(Movie)
admin.site.register(Rating)
admin.site.register(Keyword)
admin.site.register(Credit)