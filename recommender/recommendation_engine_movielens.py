import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from django.db.models import Avg, Prefetch
import pandas as pd
import os
import django
import requests
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from recommender.models import Rating, Movie, Keyword, Credit

# Load Movies with Aggregated Keywords
movies_with_keywords = Movie.objects.prefetch_related(
    'keywords'
).all()

# Initialize an empty list to store movie data
movie_data = []

# Fetch movies in small batches
batch_size = 500  # You can adjust this size if necessary
movie_queryset = Movie.objects.all()

for i in range(0, movie_queryset.count(), batch_size):
    movies_batch = movie_queryset[i:i + batch_size].prefetch_related(
        Prefetch('keywords', queryset=Keyword.objects.all())
    )
    
    # Process each movie in the batch
    for movie in movies_batch:
        movie_data.append({
            'id': movie.id,
            'title': movie.title,
            'overview': movie.overview,
            'genres': movie.genres,
            'vote_average': movie.vote_average,
            'keywords': ', '.join([kw.name for kw in movie.keywords.all()])  # Collect keywords for each movie
        })

# Convert the collected movie data into a DataFrame
movies_df = pd.DataFrame(movie_data)

# Load Ratings
ratings = Rating.objects.all().values('userId', 'movie_id', 'rating')
ratings_df = pd.DataFrame(ratings)

#########Content Based 

# Fill null values in genres, overview, and keywords
movies_df['genres'] = movies_df['genres'].fillna('')
movies_df['overview'] = movies_df['overview'].fillna('')
movies_df['keywords'] = movies_df['keywords'].fillna('')

# Combine features for the content-based model
movies_df['features'] = movies_df['genres'] + ' ' + movies_df['keywords'] + ' ' + movies_df['overview']

# Use TF-IDF Vectorizer for text features
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['features'])

# Convert TF-IDF matrix to a sparse matrix format
sparse_tfidf_matrix = csr_matrix(tfidf_matrix)

# Calculate cosine similarity on sparse matrix
content_similarity = cosine_similarity(sparse_tfidf_matrix, dense_output=False)

# # Calculate cosine similarity for content-based filtering
# content_similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)


#########Collaborative

# Pivot table for user-item ratings
user_movie_ratings = ratings_df.pivot(index='userId', columns='movie_id', values='rating').fillna(0)

# Compute collaborative similarity (user-based or item-based)
collaborative_similarity = cosine_similarity(user_movie_ratings.T)  # Item-based similarity
collaborative_similarity_df = pd.DataFrame(collaborative_similarity, index=user_movie_ratings.columns, columns=user_movie_ratings.columns)


def get_hybrid_recommendations(movie_id, top_n=10, content_weight=0.5):
    # Get index of the movie
    movie_idx = movies_df[movies_df['id'] == movie_id].index[0]
    
    # Get content-based scores
    content_scores = list(enumerate(content_similarity[movie_idx]))
    
    # Get collaborative scores
    if movie_id in collaborative_similarity_df.columns:
        collaborative_scores = collaborative_similarity_df[movie_id]
    else:
        collaborative_scores = pd.Series([0] * len(movies_df), index=movies_df.index)
    
    # Combine scores with weighting
    scores = []
    for idx, content_score in content_scores:
        collab_score = collaborative_scores[idx] if idx in collaborative_scores.index else 0
        combined_score = content_weight * content_score + (1 - content_weight) * collab_score
        scores.append((idx, combined_score))
    
    # Sort by score and get top results
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    top_movie_indices = [i[0] for i in scores[1:top_n+1]]  # Exclude the original movie
    
    # Return recommended movie titles
    recommended_movies = movies_df.iloc[top_movie_indices][['title', 'genres', 'vote_average']]
    return recommended_movies

# Get recommendations for a movie with ID=1
recommendations = get_hybrid_recommendations(movie_id=186, top_n=10, content_weight=0.7)
print(recommendations)






















# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
# import ast

# # Load the datasets
# movies_metadata = pd.read_csv('/Users/utkarsh/Downloads/archive/movies_metadata.csv')
# keywords = pd.read_csv('/Users/utkarsh/Downloads/archive/keywords.csv')
# #credits = pd.read_csv('/Users/utkarsh/Downloads/archive/credits.csv')

# # Step 3: Preprocess the Data
# # 1. Drop rows with missing essential information
# movies_metadata = movies_metadata.dropna(subset=['title', 'overview', 'release_date'])

# # 2. Filter movies with runtime >= 60 minutes
# movies_metadata = movies_metadata[movies_metadata['runtime'].apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(0) >= 60]

# # 3. Merge keywords and credits data for each movie
# movies_metadata['id'] = movies_metadata['id'].astype(str)
# keywords['id'] = keywords['id'].astype(str)
# movies_metadata = movies_metadata.merge(keywords, on='id', how='left')
# #movies_metadata = movies_metadata.merge(credits, on='id', how='left')

# # Convert JSON-like strings to lists for keywords and cast/crew
# movies_metadata['keywords'] = movies_metadata['keywords'].apply(lambda x: ' '.join([i['name'] for i in ast.literal_eval(x)]) if pd.notnull(x) else '')
# #movies_metadata['cast'] = movies_metadata['cast'].apply(lambda x: ' '.join([i['name'] for i in ast.literal_eval(x)][:3]) if pd.notnull(x) else '')
# #movies_metadata['crew'] = movies_metadata['crew'].apply(lambda x: ' '.join([i['name'] for i in ast.literal_eval(x) if i['job'] == 'Director']) if pd.notnull(x) else '')

# # 4. Combine genres, overview, keywords, and director name into a single feature
# movies_metadata['genres'] = movies_metadata['genres'].apply(lambda x: ' '.join([i['name'] for i in ast.literal_eval(x)]) if pd.notnull(x) else '')
# movies_metadata['features'] = movies_metadata['genres'] + ' ' + movies_metadata['overview'] + ' ' + movies_metadata['keywords'] #+ ' ' + movies_metadata['cast'] + ' ' + movies_metadata['crew']

# # Step 4: Build the Recommendation System

# # Use TfidfVectorizer to create a matrix of TF-IDF features
# tfidf = TfidfVectorizer(stop_words='english')
# tfidf_matrix = tfidf.fit_transform(movies_metadata['features'])

# # Compute cosine similarity
# cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# # Reset movie indices to retrieve titles easily
# movies_metadata = movies_metadata.reset_index()
# indices = pd.Series(movies_metadata.index, index=movies_metadata['title']).drop_duplicates()

# # Step 5: Recommendation Function

# def get_recommendations(title, cosine_sim=cosine_sim):
#     # Get the index of the movie that matches the title
#     idx = indices[title]

#     # Get the pairwise similarity scores of all movies with that movie
#     sim_scores = list(enumerate(cosine_sim[idx]))

#     # Sort the movies based on similarity scores
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

#     # Get the scores of the 10 most similar movies
#     sim_scores = sim_scores[1:11]

#     # Get the movie indices
#     movie_indices = [i[0] for i in sim_scores]

#     # Return the top 10 most similar movies
#     return movies_metadata['title'].iloc[movie_indices]

# # Example usage
# print(get_recommendations('The Godfather'))