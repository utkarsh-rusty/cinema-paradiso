import requests

API_KEY = 'f8951074e1c4a4f4a4404cb1093a1ac9'
BASE_URL = 'https://api.themoviedb.org/3/movie/'

def fetch_movies():
    for i in range(10):
        movie_id = i
        response = requests.get(f"{BASE_URL}{movie_id}?api_key={API_KEY}&language=en-US&page=1")
        if response.status_code == 200:
            print(response.json())
        else:
            print("Error fetching data")
            

movies = fetch_movies()
print(len(movies))
for movie in movies:
    print(movie)
