import os
import django
import requests
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()  # Initialize Django

# Now you can import your models
from recommender.models import Movie

API_KEY = 'f8951074e1c4a4f4a4404cb1093a1ac9'
BASE_URL = 'https://api.themoviedb.org/3/movie/'

def fetch_movies():
    response = requests.get(f"{BASE_URL}?api_key={API_KEY}&language=en-US&page=1")
    if response.status_code == 200:
        movies = response.json()['results']
        for movie_data in movies:
            Movie.objects.update_or_create(
                title=movie_data['title'],
                defaults={
                    'genre': movie_data['genre_ids'] if movie_data['genre_ids'] else 'N/A',
                    'release_date': movie_data['release_date'],
                    'rating': movie_data['vote_average'],
                    'overview': movie_data['overview'],
                }
            )
        print('Successfully fetched and saved movies.')
    else:
        print('Error fetching data from TMDb.')

if __name__ == "__main__":
    fetch_movies()