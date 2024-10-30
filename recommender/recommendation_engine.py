from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from django.db.models import Q
import numpy as np
import pandas as pd
import os
import django
import requests
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from recommender.models import Movie  

def content_based_recommendations(movie_title, top_n=10):
    # Get all movies
    movies = Movie.objects.all()
    # Build a dataframe of genres and ratings to create a similarity matrix
    data = [(movie.title, movie.genre, movie.rating) for movie in movies if movie.genre and movie.rating]
    
    # Combine genre and rating as text
    movies_df = pd.DataFrame(data, columns=['title', 'genre', 'rating'])
    movies_df['features'] = movies_df['genre'] + " " + movies_df['rating'].astype(str)
    
    # Compute TF-IDF matrix
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['features'])
    
    # Calculate similarity between movies
    #cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix, dense_output=False)
    
    # Find index of the movie that matches the title
    indices = pd.Series(movies_df.index, index=movies_df['title']).drop_duplicates()
    idx = indices[movie_title]

    # Get similarity scores for a single movie
    sim_scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    
    # Get top n recommendations
    similar_indices = sim_scores.argsort()[-(top_n+1):-1][::-1]
    
    # Return the top n most similar movies
    return movies_df['title'].iloc[similar_indices].tolist()

print(content_based_recommendations("The Godfather"))