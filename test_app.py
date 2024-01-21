import unittest
from app import app
from unittest.mock import patch
import mock_db

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        app.config["CLIENT_ID"] = "TEST_VALUE"
        app.config["CLIENT_SECRET"] = "TEST_VALUE"
        app.config["TENANT_ID"] = "TEST_VALUE"
        app.config['TESTING'] = True
        self.app = app.test_client()
        

    @patch("identity.web.Auth.get_user", return_value={"sub": "user"})
    @patch("db.get_movies", return_value=mock_db.get_movies())
    def test_index_page(self, mocked_auth, mocked_db):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Movie ratings', response.data)

    @patch("identity.web.Auth.get_user", return_value={"sub": "user"})
    @patch("db.get_movie_details", return_value=mock_db.get_movie_details(1))
    def test_get_movie_details(self, mocked_auth, mocked_db):
        response = self.app.get('/movies/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Movie details', response.data)

    @patch("identity.web.Auth.get_user", return_value={"sub": "user"})
    @patch("db.add_movie", return_value=None)
    def test_add_movie(self, mocked_auth, mocked_db):
        response = self.app.post('/add_movie', data={'title': 'New Movie', 'director': 'New Director'})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after adding a movie

if __name__ == '__main__':
    unittest.main()
