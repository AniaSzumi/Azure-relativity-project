import identity
import identity.web
import requests
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session

import app_config

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config.get("AUTHORITY"),
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)

movies_db = [
    {"id": 1, "title": "Movie 1", "director": "Director 1"},
    {"id": 2, "title": "Movie 2", "director": "Director 2"}
]

@app.route("/login")
def login():
    return render_template("login.html", version=identity.__version__, **auth.log_in(
        scopes=app_config.SCOPE, # Have user consent to scopes during log-in
        redirect_uri=url_for("auth_response", _external=True), # Optional. If present, this absolute URL must match your app's redirect_uri registered in Azure Portal
        ))


@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route("/")
def index():
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        # This check is not strictly necessary.
        # You can remove this check from your production code.
        return render_template('config_error.html')
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template('index.html', user=auth.get_user(), version=identity.__version__, movies=movies_db)

@app.route('/movies/<int:movie_id>')
def get_movie(movie_id):
    if not auth.get_user():
        return redirect(url_for("login"))
    movie = next((m for m in movies_db if m["id"] == movie_id), None)
    if movie:
        return render_template('movie_detail.html', movie=movie)
    else:
        return "Movie not found", 404


@app.route('/add_movie', methods=['POST'])
def add_movie():
    if not auth.get_user():
        return redirect(url_for("login"))
    title = request.form.get('title')
    director = request.form.get('director')

    new_movie = {"id": len(movies_db) + 1, "title": title, "director": director}
    movies_db.append(new_movie)

    return redirect(url_for('index'))


@app.route('/update_movie/<int:movie_id>', methods=['POST'])
def update_movie(movie_id):
    if not auth.get_user():
        return redirect(url_for("login"))
    title = request.form.get('title')
    director = request.form.get('director')

    movie = next((m for m in movies_db if m["id"] == movie_id), None)
    if movie:
        movie['title'] = title
        movie['director'] = director

    return redirect(url_for('index'))


@app.route('/delete_movie/<int:movie_id>')
def delete_movie(movie_id):
    if not auth.get_user():
        return redirect(url_for("login"))
    movie = next((m for m in movies_db if m["id"] == movie_id), None)
    if movie:
        movies_db.remove(movie)

    return redirect(url_for('index'))

@app.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('display.html', result=api_result)


if __name__ == "__main__":
    app.run()
