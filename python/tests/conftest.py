import flask
import pytest
from orson.view import create_app


@pytest.fixture()
def app():
    app = create_app({"TESTING": True})
    yield app


@pytest.fixture()
def client(app: flask.Flask):
    return app.test_client()


