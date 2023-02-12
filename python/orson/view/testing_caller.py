from .iface import Caller


class TestingCaller(Caller):

    def __init__(self):
        self.rooms = {}
        self.updated = {}

    def send_message(self, room_id, msg):

        if room_id not in self.rooms:
            # new room, it has changed
            self.rooms[room_id] = RoomSimulator(room_id)
        room = self.rooms[room_id]
        if msg['msg'] == 'enter':
            # 'client_id'
            room.client_enter(msg['client_id'])
            self.updated[room_id] = room
        elif msg['msg'] == 'leave':
            # 'client_id'
            room.client_leave(msg['client_id'])
            self.updated[room_id] = room
        elif msg['msg'] == 'update':
            # ['client_ids']
            room.clients_update(msg['client_ids'])

    def send_announcements(self, client):
        for room_id,room in self.updated.items():
            room.send_announcement(client)
        self.updated = {}



class RoomSimulator(object):

    def __init__(self, room_id):
        self.room_id = room_id
        self.clients = {}

    def client_enter(self, client_id: str):
        if client_id not in self.clients:
            self.clients[client_id] = client_id

    def client_leave(self, client_id: str):
        if client_id not in self.clients:
            del self.clients[client_id]

    def clients_update(self, client_ids):
        pass

    def send_announcement(self, client):
        msg = {
            "id": self.room_id,
            "name": "",
            "clients": self.clients
        }
        response = client.post(f"/events/alert", json=msg)




