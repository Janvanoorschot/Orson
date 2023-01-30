from flask import current_app, render_template
import datetime
from queue import Queue
from . import ClientManager

from orson.view import websockets


class RemoteRoom:
    room_id: str
    name: str
    last_seen: datetime
    clients: dict

    def __init__(self, room_id, name, t):
        self.room_id = room_id
        self.name = name
        self.last_seen = t
        self.clients = {}

    def update_clients(self, manager: ClientManager, clients):
        self.clients = {}
        for client_id in clients:
            client = manager.get_client(client_id)
            if client:
                self.clients[client.client_id] = client

    def has_clients(self, clients):
        if len(clients) != len(self.clients):
            return False
        for client_id in clients:
            if client_id not in self.clients:
                return False
        return True


class RoomKeeper:
    rooms: dict
    last_seen: dict
    max_idle_secs: int

    def __init__(self):
        self.rooms = {}
        self.last_seen = {}
        self.max_idle_secs = 60

    def has_room(self, room_id):
        return room_id in self.rooms

    def get_room(self, room_id):
        return self.rooms.get(room_id, None)

    def get_rooms(self):
        t = datetime.datetime.now()
        self.cleanup(t)
        return self.rooms

    def enter_room(self, room, client):
        # send an 'enter' message to the room, that is all.
        msg = {
            'msg': 'enter',
            'client_id': client.client_id
        }
        current_app.celery.send_task("tasks.publish_message", args=[room.room_id, msg])

    def announcement(self, manager: ClientManager, message: dict):
        # announcement from a room
        room_id = message.get("id", None)
        room_name = message.get("name", None)
        clients = message.get("clients", [])
        t = datetime.datetime.now()
        self.last_seen[room_id] = t
        # remember room state change
        is_new = self.room_is_new(room_id)
        has_changed = self.room_has_changed(room_id, clients)
        self.cleanup(t)
        # update room info
        if is_new:
            room = RemoteRoom(room_id, room_name, t)
            self.rooms[room_id] = room
        else:
            room = self.rooms[room_id]
        room.update_clients(manager, clients)
        # now inform clients if needed
        if is_new or has_changed:
            self.inform_clients(t, is_new)

    def room_is_new(self, room_id) -> bool:
        return room_id not in self.rooms

    def room_has_changed(self, room_id, clients) -> bool:
        if self.room_is_new(room_id):
            return True
        room = self.rooms[room_id]
        return not room.has_clients(clients)

    def cleanup(self, t):
        remove = []
        for id, ls_t in self.last_seen.items():
            if (t - ls_t).total_seconds() > self.max_idle_secs:
                remove.append(id)
        for id in remove:
            del self.rooms[id]
            del self.last_seen[id]

    def inform_clients(self, t, is_new):
        html_blob = self.format_announcement(t, is_new)
        for ws, content in websockets.items():
            queue: Queue = content[0]
            queue.put(html_blob)

    def format_announcement(self, t, is_new) -> str:
        # send the complete rooms/clients matrix back
        map = {
            'rooms': self.rooms,
        }
        return render_template("rooms_matrix.html", **map)
