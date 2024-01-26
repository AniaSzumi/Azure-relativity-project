import pyodbc
import os

columns = ['id', 'title', 'director', 'rating', 'number_of_ratings']

def get_connection():
    USERNAME = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASSWORD")
    SERVER = os.getenv("DB_SERVER")
    DATABASE = os.getenv("DB")
    connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={SERVER};Database={DATABASE};Uid={USERNAME};Pwd={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    # connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    return pyodbc.connect(connection_string)

def get_movies():
    conn = get_connection()
    cur = conn.cursor()

    select_movies_query = "SELECT * FROM Movies"
    cur.execute(select_movies_query)
    movies_struct = [ dict(zip(columns,row)) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return movies_struct

def get_movie_details(movie_id):
    conn = get_connection()
    cur = conn.cursor()

    select_movie_query = f"SELECT * FROM Movies WHERE ID = {movie_id}"
    cur.execute(select_movie_query)
    row = cur.fetchone()
    movie = None
    if row:
        movie = dict(zip(columns,row))

    cur.close()
    conn.close()
    return movie

def add_movie(form):
    conn = get_connection()
    cur = conn.cursor()
        
    add_movie_statement = f"INSERT INTO Movies(Title, Director) VALUES (? , ?)"
    count = cur.execute(add_movie_statement, form.get('title'), form.get('director')).rowcount

    conn.commit()
    cur.close()
    conn.close()
    return count

def add_movie_rating(movie_id, rating):
    conn = get_connection()
    cur = conn.cursor()

    select_movie_query = f"SELECT * FROM Movies WHERE ID = {movie_id}"
    cur.execute(select_movie_query)
    row = cur.fetchone()
    movie = dict(zip(columns,row))

    new_number_of_ratings = movie['number_of_ratings'] + 1
    new_rating = (movie['rating']*movie['number_of_ratings'] + rating) / new_number_of_ratings

    add_rating_statement = f"INSERT INTO Ratings (MovieId, Rating) VALUES({movie_id}, {rating})"
    count = cur.execute(add_rating_statement).rowcount

    update_movie_statement = f"UPDATE Movies SET Rating = {new_rating}, NumberOfRatings = {new_number_of_ratings} WHERE ID = {movie_id}"
    cur.execute(update_movie_statement)

    conn.commit()
    cur.close()
    conn.close()
    return count
