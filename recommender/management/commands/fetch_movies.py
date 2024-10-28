import requests

API_KEY = 'f8951074e1c4a4f4a4404cb1093a1ac9'
BASE_URL = 'https://api.themoviedb.org/3/movie/popular'

def fetch_movies():
    response = requests.get(f"{BASE_URL}?api_key={API_KEY}&language=en-US&page=1")
    if response.status_code == 200:
        return response.json()['results']
    else:
        print("Error fetching data")
        return []

movies = fetch_movies()
for movie in movies:
    print(movie)
    break