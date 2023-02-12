from flask.testing import FlaskClient
from flask import session
import tests


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
    assert json[0]['room_id'] == "1234"
    assert json[0]['room_name'] == "room1"



def test_enter_room(client: FlaskClient):
    with client:
        # create room
        msg = {
            "id": "1234",
            "name": "room1",
            "clients": {}
        }
        response = client.post(f"/events/alert", json=msg)
        assert response.status_code == 200
        # clear client_id ( creating room created client_id '0')
        session['client_id'] = "invalid"
        # test if the room was detected
        response = client.get(f'/rooms?json')
        assert response.status_code == 200
        # enter this room
        c = tests.caller
        response = client.post(f"/enter_room/1234")
        assert response.status_code == 200
        # trigger the caller to send its announcements
        tests.caller.send_announcements(client)
        # test if the client was detected
        response = client.get(f'/rooms?json')
        assert response.status_code == 200


