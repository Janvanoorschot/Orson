from .iface import Caller


class TestingCaller(Caller):

    def __init__(self):
        self.rooms = {}
        self.announcements = {}

    def send_message(self, room_id, msg):

        if room_id not in self.rooms:
            # new room, it has changed
            self.rooms[room_id] = RoomSimulator(room_id)
        room = self.rooms[room_id]
        if msg['msg'] == 'enter':
            # 'client_id'
            room.client_enter(msg['client_id'])
            self.announcements[room_id] = room.get_announcement()
        elif msg['msg'] == 'leave':
            # 'client_id'
            room.client_leave(msg['client_id'])
            self.announcements[room_id] = room.get_announcement()
        elif msg['msg'] == 'update':
            # ['client_ids']
            room.clients_update(msg['client_ids'])

    def get_announcements(self):
        result = self.announcements
        self.announcements = {}
        return result



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

    def get_announcement(self):
        msg = {
            "id": self.room_id,
            "name": "",
            "clients": self.clients
        }
        return msg




