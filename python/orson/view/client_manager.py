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
    room: "RemoteRoom"
    target_room: "RemoteRoom"

    def __init__(self, client_id, name):
        self.client_id = client_id
        self.name = name
        self.created_at = datetime.datetime.now()
        self.reset()

    def reset(self):
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

    def event(self, evt, client, *args):
        pass

    ######################################################################################
    # Event functions called by other entities
    def evt_room_has_new_client(self, room, client_id):
        # the client has entered the room
        if self.get_client(client_id):
            self.event(EVT_Alert_EnteredRoom, self.get_client(client_id), room)

    def evt_room_has_lost_client(self, room, client_id):
        # the client has left the room
        if self.get_client(client_id):
            self.event(EVT_Alert_LeftRoom, self.get_client(client_id), room)

    def evt_room_lost(self, room):
        # a room has been blasted from space
        for client_id, client in self.clients.items():
            if client.room == room or client.target_room == room:
                self.event(EVT_Timer_RoomDisappeared, self.get_client(client_id), room)
                client.reset()

    def enter_room(self, client, room):
        # client requests to enter a room
        self.event(EVT_REST_EnterRoom, client, room)
        # send an 'enter' message to the room
        msg = {
            'msg': 'enter',
            'client_id': client.client_id
        }
        current_app.celery.send_task("tasks.publish_message", args=[room.room_id, msg])

    def leave_room(self, client: Client):
        # client requests to leave a room
        self.event(EVT_REST_EnterRoom, client)
        # send a 'leave' message to the room
        msg = {
            'msg': 'leave',
            'client_id': client.client_id
        }
        if client.in_room():
            current_app.celery.send_task("tasks.publish_message", args=[client.room.room_id, msg])
