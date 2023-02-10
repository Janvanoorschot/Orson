from orson.view import create_app


def test_config():
    assert create_app({'TESTING': True}).testing
    # assert not create_app().testing
