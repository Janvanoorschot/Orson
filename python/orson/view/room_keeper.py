import datetime
from queue import Queue, Empty
from . import websockets


class RoomKeeper:

    rooms: dict
    lastseen: dict
    max_idle_secs: int

    def __init__(self):
        self.rooms = {}
        self.lastseen = {}
        self.max_idle_secs = 60

    def announcement(self, message: dict):
        # announcement from a room
        id = message.get("id", None)
        name = message.get("name", None)
        t = datetime.datetime.now()
        self.lastseen[id] = t
        if self.room_has_changed(id, message):
            self.rooms[id] = name
            self.cleanup(t)
            self.inform_clients(message)

    def room_has_changed(self, id, message) -> bool:
        if id not in self.rooms:
            return True
        return True

    def cleanup(self, t):
        remove = []
        for id,ls_t in self.lastseen.items():
            if (t - ls_t).total_seconds() > self.max_idle_secs:
                remove.append(id)
        for id in remove:
            del self.rooms[id]
            del self.lastseen[id]

    def inform_clients(self, message):
        for ws, content in websockets.items():
            queue: Queue = content[0]
            html_blob = self.format_announcement(message)
            queue.put(html_blob)

    def format_announcement(self, message) -> str:
        val = f"<li>{message['id']}/{message['name']}/{message['t']}</li>"
        blob = f"<div id=\"notifications\" hx-swap-oob=\"beforeend\">{val}</div>"
        return blob

    def get_rooms(self):
        t = datetime.datetime.now()
        self.cleanup(t)
        return self.rooms
