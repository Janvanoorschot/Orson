import datetime


class RoomKeeper:

    rooms: dict
    lastseen: dict
    max_idle_secs: int

    def __init__(self):
        self.rooms = {}
        self.lastseen = {}
        self.max_idle_secs = 60

    def announcement(self, message: dict):
        id = message.get("id", None)
        name = message.get("name", None)
        t = datetime.datetime.now()
        self.lastseen[id] = t
        self.rooms[id] = name

    def cleanup(self, t):
        remove = []
        for id,ls_t in self.lastseen.items():
            if (t - ls_t).total_seconds() > self.max_idle_secs:
                remove.append(id)
        for id in remove:
            del self.rooms[id]
            del self.lastseen[id]

    def get_rooms(self):
        t = datetime.datetime.now()
        self.cleanup(t)
        return self.rooms
