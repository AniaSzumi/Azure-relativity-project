import identity
import identity.web
import requests
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
import db
import app_config

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

middleware = FlaskMiddleware(app)

exporter = metrics_exporter.new_metrics_exporter(
    enable_standard_metrics=False,
    connection_string=app.config['APPLICATIONINSIGHTS_CONNECTION_STRING'])

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string=app.config['APPLICATIONINSIGHTS_CONNECTION_STRING']))
logger.setLevel(logging.INFO)

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

def sum(a: int, b: int) -> int:
    return a + b

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
        logger.warning("Login failed")
        return render_template("auth_error.html", result=result)
    logger.info("Login success")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    logger.info("Logout")
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route("/")
def index():
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        # This check is not strictly necessary.
        # You can remove this check from your production code.
        return render_template('config_error.html')
    if not auth.get_user():
        return redirect(url_for("login"))
    db_movies = db.get_movies()
    logger.info(f"Movies from db: {db_movies}")
    return render_template('index.html', user=auth.get_user(), movies=db_movies)
    # return render_template('index.html', movies=db_movies)

@app.route("/exception")
def exception():
    a = 2
    b = "a"

    try:
        sum(a,b)
    except Exception:
        logger.exception(Exception)

    return redirect(url_for("index"))


@app.route('/movies/<int:movie_id>')
def get_movie(movie_id):
    if not auth.get_user():
        return redirect(url_for("login"))
    movie = db.get_movie_details(movie_id)
    if movie:
        return render_template('movie_detail.html', movie=movie, user=auth.get_user())
    else:
        logger.error(f"Movie with id {movie_id} not found")
        return "Movie not found", 404

@app.route('/add_movie')
def add_movie_form():
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template('add_movie.html', user=auth.get_user())

@app.route('/add_movie', methods=['POST'])
def add_movie():
    db.add_movie(request.form)

    return redirect(url_for('index'))

@app.route('/add_rating/<int:movie_id>', methods=['POST'])
def add_rating(movie_id):
    rating = int(request.form.get('rating'))
    if rating > 10 or rating < 0:
        return "Rating must be in range [1, 10]", 400
    db.add_movie_rating(movie_id, rating)
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
