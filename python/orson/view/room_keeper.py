import datetime
import orson.view
from . import RemoteRoom, RoomKeeper, Client, Caller


class RemoteRoomImpl(RemoteRoom):
    room_id: str
    name: str
    last_seen: datetime
    clients: dict

    def __init__(self, room_id, name, t):
        self.room_id = room_id
        self.name = name
        self.last_seen = t
        self.clients = {}

    def get_room_id(self):
        return self.room_id

    def get_room_name(self):
        return self.name

    def get_clients(self):
        return self.clients

    def client_enter(self, client: Client):
        if client.get_client_id() not in self.clients:
            self.clients[client.get_client_id()] = client

    def client_leave(self, client: Client):
        if client.get_client_id() in self.clients:
            del self.clients[client.get_client_id()]


class RoomKeeperImpl(RoomKeeper):

    caller: Caller
    rooms: dict
    last_seen: dict
    max_idle_secs: int

    def __init__(self, app, caller: Caller):
        self.app = app
        self.caller = caller
        self.rooms = {}
        self.last_seen = {}
        self.max_idle_secs = 60

    def has_room(self, room_id) -> bool:
        return room_id in self.rooms

    def get_room(self, room_id) -> RemoteRoom:
        return self.rooms.get(room_id, None)

    def get_rooms(self) -> dict:
        return self.rooms

    def announcement(self, message: dict):
        # announcement from a room
        room_id = message.get("id", None)
        room_name = message.get("name", None)
        client_ids = message.get("clients", [])
        t = datetime.datetime.now()
        self.last_seen[room_id] = t
        # remember room state change
        is_new = self.room_is_new(room_id)
        self.cleanup(t)
        # update room info
        if is_new:
            room = RemoteRoomImpl(room_id, room_name, t)
            self.rooms[room_id] = room
        else:
            room = self.rooms[room_id]
        self.update_clients(room, client_ids)
        self.inform_room(room)

    def get_announcements(self):
        return self.caller.get_announcements()

    def update_clients(self, room, client_ids):
        """ Update the client-list in this room and inform the client_manager about changes """
        for client_id in client_ids:
            if client_id not in room.clients:
                # new client
                self.app.extensions["orson"]["manager"].evt_room_has_new_client(room, client_id)
        for client_id in room.clients.keys():
            if client_id not in client_ids:
                # lost client
                self.app.extensions["orson"]["manager"].evt_room_has_lost_client(room, client_id)
        # take over the new list of clients
        room.clients = {}
        for client_id in client_ids:
            client = self.app.extensions["orson"]["manager"].get_client(client_id)
            if client is None:
                """ unknown client, should we create one?"""
                client = self.app.extensions["orson"]["manager"].create_client(client_id)
            room.clients[client.get_client_id()] = client

    def room_is_new(self, room_id) -> bool:
        return room_id not in self.rooms

    def cleanup(self, t: datetime):
        remove = []
        for room_id, ls_t in self.last_seen.items():
            if (t - ls_t).total_seconds() > self.max_idle_secs:
                remove.append(room_id)
        for room_id in remove:
            # inform the client_manager about the lost clients
            room = self.get_room(room_id)
            for client_id, client in room.get_clients().items():
                self.app.extensions["orson"]["manager"].evt_room_has_lost_client(room, client_id)
            self.app.extensions["orson"]["manager"].evt_room_lost(room)
            # remove the room from our inventory
            del self.rooms[room_id]
            del self.last_seen[room_id]

    def inform_room(self, room: RemoteRoom):
        """ send client-heartbeat message to the room"""
        msg = {
            'msg': 'update',
            'client_ids': [client_id for client_id in room.get_clients()]
        }
        self.caller.send_message(room.get_room_id(), msg)

