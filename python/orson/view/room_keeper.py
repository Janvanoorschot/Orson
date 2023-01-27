import json

from flask import current_app
import datetime
from queue import Queue, Empty

from orson.view import websockets, MessageQueue


class RoomKeeper:

    rooms: dict
    clients: dict
    last_seen: dict
    max_idle_secs: int

    def __init__(self):
        self.rooms = {}
        self.last_seen = {}
        self.max_idle_secs = 60
        self.clients = {}

    def has_room(self, room_id):
        return room_id in self.rooms

    def get_room(self, room_id):
        return self.rooms.get(room_id, None)

    def get_rooms(self):
        t = datetime.datetime.now()
        self.cleanup(t)
        return self.rooms

    def announcement(self, message: dict):
        # announcement from a room
        id = message.get("id", None)
        name = message.get("name", None)
        clients = message.get("clients", [])
        t = datetime.datetime.now()
        self.last_seen[id] = t
        if self.room_has_changed(id, message):
            self.rooms[id] = name
            self.clients[id] = clients
            self.cleanup(t)
            self.inform_clients(t,id,name,clients)

    def enter_room(self, room_id, client_id):
        # send an 'enter' message to the room, that is all
        msg = {
            'msg': 'enter',
            'client_id': client_id
        }
        current_app.celery.send_task("tasks.publish_message", args=[room_id, msg])

    def room_has_changed(self, id, message) -> bool:
        if id not in self.rooms:
            return True
        return True

    def cleanup(self, t):
        remove = []
        for id,ls_t in self.last_seen.items():
            if (t - ls_t).total_seconds() > self.max_idle_secs:
                remove.append(id)
        for id in remove:
            del self.rooms[id]
            del self.last_seen[id]

    def inform_clients(self, t, id, name, clients):
        for ws, content in websockets.items():
            queue: Queue = content[0]
            html_blob = self.format_announcement(t, id, name, clients)
            queue.put(html_blob)

    def format_announcement(self,t, id, name, clients) -> str:
        clients_str = "\n".join([f"<li>{client_id}[{clients[client_id]}]</li>" for client_id in clients])
        val = f"<li>{id}/{name}/{t}<ul>{clients_str}</ul></li>"
        blob = f"<div id=\"notifications\" hx-swap-oob=\"beforeend\">{val}</div>"
        return blob

