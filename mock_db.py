movies = [
    {"id": 1, "title": "Movie 1", "director": "Director 1", "rating": 4.6, "number_of_ratings": 10},
    {"id": 2, "title": "Movie 2", "director": "Director 2", "rating": 4.6, "number_of_ratings": 10}
]

columns = ['id', 'title', 'director', 'rating', 'number_of_ratings']

def get_movies():
    return movies

def get_movie_details(movie_id):
    movie = next((m for m in movies if m["id"] == movie_id), None)
    return movie

def add_movie(form):
    new_movie = {"id": len(movies) + 1, "title": form.get('title'), "director": form.get('director')}
    movies.append(new_movie)

def add_movie_rating(movie_id, rating):
   pass
