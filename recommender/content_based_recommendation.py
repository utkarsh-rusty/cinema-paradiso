import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
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
# # Load Movies from Django ORM into DataFrame
# movies = Movie.objects.all()
# movies_df = pd.DataFrame(list(movies.values('id', 'title', 'overview', 'genres', 'vote_average')))

# Add keywords as a string to each movie
def get_keywords(movie):
    return ', '.join(kw.name for kw in Keyword.objects.filter(movie=movie))

movies_df['keywords'] = movies_df['id'].apply(lambda x: get_keywords(Movie.objects.get(id=x)))

# Combine relevant text fields into a single "content" feature
movies_df['content'] = movies_df['overview'].fillna('') + ' ' + movies_df['genres'].fillna('') + ' ' + movies_df['keywords'].fillna('')

# Compute TF-IDF Matrix
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['content'])

# Normalize vote_average
scaler = MinMaxScaler()
movies_df['normalized_vote_average'] = scaler.fit_transform(movies_df[['vote_average']].fillna(0))

# Content-Based Recommendation Function
def get_content_based_recommendations(movie_title, top_n=10,  weight_factor=0.2):
    # Standardize the input title for comparison
    movie_title = movie_title.strip().lower()
    
    # Standardize all titles in the DataFrame
    movies_df['title_lower'] = movies_df['title'].str.lower().str.strip()

    # Check if the movie title exists in the dataset
    if movie_title not in movies_df['title_lower'].values:
        raise ValueError(f"Movie '{movie_title}' not found in the dataset.")
    
    # Get index of the movie by title
    movie_idx = movies_df[movies_df['title_lower'] == movie_title].index[0]

    # Get similarity scores for a single movie
    sim_scores = cosine_similarity(tfidf_matrix[movie_idx], tfidf_matrix).flatten()

    # Adjust similarity scores with normalized vote_average
    adjusted_scores = (1 - weight_factor) * sim_scores + weight_factor * movies_df['normalized_vote_average']
    
    # Get top n recommendations, excluding the movie itself
    similar_indices = adjusted_scores.argsort()[-(top_n + 1):-1][::-1]  # Sort and exclude the original movie
    
    # Get recommended movie titles
    recommended_movies = movies_df.iloc[similar_indices][['title', 'genres', 'vote_average']]
    
    # Drop 'title_lower' before returning to clean up
    movies_df.drop(columns='title_lower', inplace=True)
    
    return recommended_movies

print(get_content_based_recommendations('La la land'))