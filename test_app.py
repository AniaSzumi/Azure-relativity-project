import unittest
from app import app, movies_db
from unittest.mock import patch

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        app.config["CLIENT_ID"] = "TEST_VALUE"
        app.config["CLIENT_SECRET"] = "TEST_VALUE"
        app.config["TENANT_ID"] = "TEST_VALUE"
        app.config['TESTING'] = True
        self.app = app.test_client()
        

    @patch("identity.web.Auth.get_user", return_value={"sub": "user"})
    def test_index_page(self, mocked_auth):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Movie Management', response.data)

    @patch("identity.web.Auth.get_user", return_value={"sub": "user"})
    def test_get_movie_details(self, mocked_auth):
        response = self.app.get('/movies/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Movie Details', response.data)

    @patch("identity.web.Auth.get_user", return_value={"sub": "user"})
    def test_add_movie(self, mocked_auth):
        initial_count = len(movies_db)
        response = self.app.post('/add_movie', data={'title': 'New Movie', 'director': 'New Director'})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after adding a movie
        self.assertEqual(len(movies_db), initial_count + 1)

    @patch("identity.web.Auth.get_user", return_value={"sub": "user"})
    def test_update_movie(self, mocked_auth):
        movie_id = 1
        response = self.app.post(f'/update_movie/{movie_id}', data={'title': 'Updated Title', 'director': 'Updated Director'})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after updating a movie
        updated_movie = next((m for m in movies_db if m['id'] == movie_id), None)
        self.assertIsNotNone(updated_movie)
        self.assertEqual(updated_movie['title'], 'Updated Title')
        self.assertEqual(updated_movie['director'], 'Updated Director')

    @patch("identity.web.Auth.get_user", return_value={"sub": "user"})
    def test_delete_movie(self, mocked_auth):
        initial_count = len(movies_db)
        movie_id = initial_count
        response = self.app.get(f'/delete_movie/{movie_id}')
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after deleting a movie
        self.assertEqual(len(movies_db), initial_count - 1)


if __name__ == '__main__':
    unittest.main()
