from flask.testing import FlaskClient


def test_get_json_room(client: FlaskClient):
    response = client.get(f'/rooms?json')
    assert response.status_code == 200
    json = response.json
    assert len(json) == 0


def test_create_room(client: FlaskClient):
    # send a message that should create a room
    msg = {
        "id": "1234",
        "name": "room1",
        "clients": {}
    }
    response = client.post(f"/events/alert", json=msg)
    assert response.status_code == 200

    # test if the room was detected
    response = client.get(f'/rooms?json')
    assert response.status_code == 200
    json = response.json
    assert len(json) == 1
