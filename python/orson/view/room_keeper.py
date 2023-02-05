import datetime
from . import RemoteRoom, RoomKeeper, ClientManager


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

    def get_clients(self):
        return self.clients

    def has_clients(self, client_ids):
        # check if the client lists are the same
        if len(client_ids) != len(self.clients):
            return False
        for client_id in client_ids:
            if client_id not in self.clients:
                return False
        return True


class RoomKeeperImpl(RoomKeeper):

    rooms: dict
    last_seen: dict
    max_idle_secs: int

    def __init__(self):
        self.rooms = {}
        self.last_seen = {}
        self.max_idle_secs = 60

    def has_room(self, room_id) -> bool:
        return room_id in self.rooms

    def get_room(self, room_id) -> RemoteRoom:
        return self.rooms.get(room_id, None)

    def get_rooms(self) -> dict:
        return self.rooms

    def update_clients(self, manager, room, client_ids):
        """ Update the client-list in this room and inform the client_manager about changes """
        for client_id in client_ids:
            if client_id not in room.clients:
                # new client
                manager.evt_room_has_new_client(self, client_id)
        for client_id in room.clients.keys():
            if client_id not in client_ids:
                # lost client
                manager.evt_room_has_lost_client(self, client_id)
        # take over the new list of clients
        room.clients = {}


        for client_id in client_ids:
            client = manager.get_client(client_id)
            if client is not None:
                print("here")
                room.clients[client.get_client_id()] = client

    def announcement(self, manager: ClientManager, message: dict):
        # announcement from a room
        room_id = message.get("id", None)
        room_name = message.get("name", None)
        client_ids = message.get("clients", [])
        t = datetime.datetime.now()
        self.last_seen[room_id] = t
        # remember room state change
        is_new = self.room_is_new(room_id)
        has_changed = self.room_has_changed(room_id, client_ids)
        self.cleanup(manager, t)
        # update room info
        if is_new:
            room = RemoteRoomImpl(room_id, room_name, t)
            self.rooms[room_id] = room
        else:
            room = self.rooms[room_id]
        self.update_clients(manager, room, client_ids)

    def room_is_new(self, room_id) -> bool:
        return room_id not in self.rooms

    def room_has_changed(self, room_id, clients) -> bool:
        if self.room_is_new(room_id):
            return True
        room = self.rooms[room_id]
        return not room.has_clients(clients)

    def cleanup(self, manager: ClientManager, t: datetime):
        remove = []
        for room_id, ls_t in self.last_seen.items():
            if (t - ls_t).total_seconds() > self.max_idle_secs:
                remove.append(room_id)
        for room_id in remove:
            # inform the client_manager about the lost clients
            room = self.get_room(room_id)
            for client_id, client in room.get_clients().items():
                manager.evt_room_has_lost_client(room, client_id)
            manager.evt_room_lost(room)
            # remove the room from our inventory
            del self.rooms[room_id]
            del self.last_seen[room_id]

