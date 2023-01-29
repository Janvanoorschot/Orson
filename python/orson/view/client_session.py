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


