from django.db import transaction
import pandas as pd
import os
import django
import requests
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
error = []
from recommender.models import Movie, Rating, Keyword, Credit  

# Delete all existing entries in the Movie model
Rating.objects.all().delete()

print("All existing ratings have been deleted.")

# Paths to the data files
movies_metadata_path = "/Users/utkarsh/Downloads/archive/movies_metadata.csv"
keywords_path = "/Users/utkarsh/Downloads/archive/keywords.csv"
credits_path = "/Users/utkarsh/Downloads/archive/credits.csv"
ratings_path = "/Users/utkarsh/Downloads/archive/ratings.csv"

# Load Movies Metadata
movies_metadata = pd.read_csv(movies_metadata_path, low_memory=False)
keywords = pd.read_csv(keywords_path)
credits = pd.read_csv(credits_path)
ratings = pd.read_csv(ratings_path)

# Clean and format data as needed
# Ensure IDs are integers
movies_metadata['id'] = pd.to_numeric(movies_metadata['id'], errors='coerce')
keywords['id'] = pd.to_numeric(keywords['id'], errors='coerce')
credits['id'] = pd.to_numeric(credits['id'], errors='coerce')
ratings['movieId'] = pd.to_numeric(ratings['movieId'], errors='coerce')

# Drop rows with invalid IDs
movies_metadata.dropna(subset=['id'], inplace=True)
keywords.dropna(subset=['id'], inplace=True)
credits.dropna(subset=['id'], inplace=True)
ratings.dropna(subset=['movieId'], inplace=True)

# Convert genres from JSON string to a comma-separated string
import ast

def parse_genres(genres_str):
    try:
        genres = [genre['name'] for genre in ast.literal_eval(genres_str)]
        return ', '.join(genres)
    except (ValueError, SyntaxError):
        return ''

movies_metadata['genres'] = movies_metadata['genres'].apply(parse_genres)

# Define the data loading function with transactions for database integrity
#@transaction.atomic
def load_data():
    # Load movies into the database
    # for _, row in movies_metadata.iterrows():
    #     try:
    #         movie, created = Movie.objects.get_or_create(
    #             id=row['id'],
    #             defaults={
    #                 'title': row['title'],
    #                 'overview': row.get('overview', ''),
    #                 'runtime': pd.to_numeric(row.get('runtime'), errors='coerce'),
    #                 'release_date': pd.to_datetime(row.get('release_date'), errors='coerce').date() if pd.notnull(row.get('release_date')) else None,
    #                 'genres': row.get('genres', ''),
    #                 'vote_average': pd.to_numeric(row.get('vote_average'), errors='coerce'),
    #                 'vote_count': pd.to_numeric(row.get('vote_count'), errors='coerce')
    #             }
    #         )
    #         print(f"Loaded movie: {row['title']}")
    #     except:
    #         print(f"Error Loaded movie: {row['title']}")

    # Get all existing movie IDs for validation
    existing_movie_ids = set(Movie.objects.values_list('id', flat=True))

    # Load ratings into the database
    for _, row in ratings.iterrows():
        try:
            if row['movieId'] in existing_movie_ids: 
                Rating.objects.create(
                    userId=row['userId'],
                    movie_id=row['movieId'],  # Ensure the foreign key matches the movie ID in `Movie`
                    rating=row['rating']
                )
                print(f"Loaded rating: {row['movieId']}")
        except Exception as error:
            print(f"error Loaded rating: {row['movieId']} error is {error}")

    # Load keywords into the database
    # for _, row in keywords.iterrows():
    #     try:
    #         if row['id'] in existing_movie_ids:
    #             for keyword in ast.literal_eval(row['keywords']):
    #                 Keyword.objects.create(
    #                     movie_id=row['id'],
    #                     name=keyword['name']
    #                 )
    #             print(f"Loaded keywords: {row['id']}")
    #     except:
    #         print(f"error Loaded keywords: {row['id']}")

    #Load credits into the database
    # for _, row in credits.iterrows():
    #     try:
    #         if row['id'] in existing_movie_ids:
    #             for cast in ast.literal_eval(row['cast']):
    #                 Credit.objects.create(
    #                     movie_id=row['id'],
    #                     name=cast['name'],
    #                     role=cast['character']  # or 'job' for crew roles if needed
    #                 )
    #             print(f"Loaded credits: {row['id']}")
    #     except:
    #         print(f"error Loaded credits: {row['id']}")

if __name__ == "__main__":
    load_data()
    print("Data loading completed.")