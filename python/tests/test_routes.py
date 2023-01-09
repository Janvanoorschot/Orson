from flask.testing import FlaskClient


def test_hello(client: FlaskClient):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'


def test_fav_icon(client: FlaskClient):
    response = client.get('/favicon.ico')
    assert response.status_code == 200


def test_content(client: FlaskClient):
    response = client.get('/')
    assert ("Jan van Oorschot" in response.data.decode())


def test_rooms(client: FlaskClient):
    response = client.get('/rooms')
    assert response.status_code == 200



