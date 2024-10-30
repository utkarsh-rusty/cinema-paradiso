import pandas as pd
import os
import django
import requests
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
error = []
from recommender.models import Movie  

# Delete all existing entries in the Movie model
Movie.objects.all().delete()

print("All existing movies have been deleted.")

def load_imdb_data():
    # Load basics data
    basics_df = pd.read_csv('/Users/utkarsh/Downloads/IMDb Data/title.basics.tsv', sep='\t', dtype=str)
    
    # Load ratings data
    ratings_df = pd.read_csv('/Users/utkarsh/Downloads/IMDb Data/title.ratings.tsv', sep='\t', dtype=str)
    
    # Merge the dataframes on the 'tconst' column to combine ratings with basics
    movies_df = pd.merge(basics_df, ratings_df, on='tconst', how='inner')
    
    # Filter for movies only
    movies_df = movies_df[movies_df['titleType'] == 'movie']
    
    # Drop rows with missing essential information
    movies_df = movies_df.dropna(subset=['primaryTitle', 'averageRating', 'startYear'])

    # Convert 'runtimeMinutes' to numeric, forcing errors to NaN for non-numeric values
    movies_df['runtimeMinutes'] = pd.to_numeric(movies_df['runtimeMinutes'], errors='coerce')

    # Drop rows where 'runtimeMinutes' is NaN (non-numeric values converted to NaN)
    movies_df = movies_df.dropna(subset=['runtimeMinutes'])

    # Filter out movies with runtime less than 60 minutes
    movies_df = movies_df[movies_df['runtimeMinutes'] >= 60]
    
    # Iterate over the DataFrame and save each movie to the database
    for _, row in movies_df.iterrows():
        try:
            Movie.objects.update_or_create(
                title=row['primaryTitle'],
                defaults={
                    'genre': row['genres'],
                    'release_date': row['startYear'],
                    'rating': row['averageRating'],
                    'overview': row.get('overview', ''),
                    'runtime': row['runtimeMinutes'],
                    'num_votes': row['numVotes']
                }
            )
            print(f"Loaded movie: {row['primaryTitle']}")
        except:
            error.append(row)
            print(f"Error Loaded movie: {row['primaryTitle']}")
        

# Run the function to load data
load_imdb_data()
print(error)