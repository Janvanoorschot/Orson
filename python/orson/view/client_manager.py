from flask import current_app
import uuid
import datetime

STATE_NOWHERE = 0
STATE_ROOMSELECTED = 1
STATE_INROOM = 2
STATE_LEAVINGROOM = 3

EVT_REST_EnterRoom = 0
EVT_REST_LeaveRoom = 1
EVT_Alert_EnteredRoom = 2
EVT_Alert_LeftRoom = 3
EVT_Timer_RoomDisappeared = 4


class Client:

    client_id: str
    name: str
    created_at: datetime
    state: int
    room: str
    target_room: str

    def __init__(self, client_id, name):
        self.client_id = client_id
        self.name = name
        self.created_at = datetime.datetime.now()
        self.state = STATE_NOWHERE
        self.room = None
        self.target_room = None

    def in_room(self):
        return self.state == STATE_INROOM

    def handle_event(self, event):
        pass

    def action_something(self):
        pass


class ClientManager:

    clients: dict

    def __init__(self):
        self.clients = {}
        self.zero = Client("0", "client_0")

    def has_client(self, client_id) -> bool:
        return client_id in self.clients

    def get_client(self, client_id) -> Client:
        return self.clients.get(client_id, None)

    def zero_client(self) -> Client:
        return self.zero

    def create_client(self) -> Client:
        client_id = str(uuid.uuid4())
        client_name = f"client[{len(self.clients)}]"
        self.clients[client_id] = Client(client_id, client_name)
        return self.clients[client_id]

    ######################################################################################
    # Event functions called by other entities
    def evt_room_has_new_client(self, room, client_id):
        pass

    def evt_room_has_lost_client(self, room, client_id):
        pass

    def evt_room_lost(self, room):
        pass

    def enter_room(self, client, room):
        # send an 'enter' message to the room, that is all.
        msg = {
            'msg': 'enter',
            'client_id': client.client_id
        }
        current_app.celery.send_task("tasks.publish_message", args=[room.room_id, msg])

    def leave_room(self, client):
        # send an 'leave' message to the room, that is all.
        msg = {
            'msg': 'enter',
            'client_id': client.client_id
        }
        current_app.celery.send_task("tasks.publish_message", args=[room.room_id, msg])
