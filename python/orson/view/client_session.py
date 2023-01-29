import datetime
from flask import render_template
from . import Client, ClientManager, RoomKeeper


class ClientSession:

    client: Client
    keeper: RoomKeeper
    manager: ClientManager

    def __init__(self, client, keeper, manager):
        self.client = client
        self.keeper = keeper
        self.manager = manager

    @classmethod
    def old_rooms(cls, keeper):
        rooms = keeper.get_rooms()
        lines = []
        for room_id, name in rooms.items():
            url = f"/enter_room/{room_id}"
            lines.append(f'''<div hx-get="{url}" hx-trigger="click" hx-target="#debugging" class="list-group-item list-group-item-action">{name}</div>''')
        return f'''<ul class="list-group">\n{" ".join(lines)}\n</ul>'''

    @classmethod
    def rooms(cls, keeper):
        map = {
            'rooms': keeper.get_rooms()
        }
        return render_template("rooms.html", **map)

    def enter_room(self, room_id):
        if self.keeper.has_room(room_id):
            room = self.keeper.get_room(room_id)
            self.keeper.enter_room(room_id, self.client.client_id)
            return f'''<div id="messages">Entering room {room}</div>'''
        else:
            return f'''<div id="messages">Trying to enter unknown room {room_id}</div>'''


