from orson.view import create_app, close_app
from flask.testing import FlaskClient


def test_config():
    assert not create_app().testing
    close_app()
    assert create_app({'TESTING': True}).testing
    close_app()


def test_hello(client: FlaskClient):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'