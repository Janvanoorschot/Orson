import datetime


class ClientSession:

    client_id: str
    created_at: datetime

    def __init__(self, client_id, created_at):
        self.client_id = client_id
        self.created_at = created_at


    @classmethod
    def rooms(cls, keeper):
        rooms = keeper.get_rooms()
        lines = []
        for id, name in rooms.items():
            # lines.append(f"""<li id="{id}" class="list-group-item">{name}</li>""")
            url = f"/enter_room/{id}"
            # lines.append(f"""<a hx-post="{url}" hx-trigger="click" hx-target={id} class="list-group-item list-group-item-action">{name}</a>""")
            lines.append(f'''<div hx-get="{url}" hx-trigger="click" hx-target="#debugging" class="list-group-item list-group-item-action">{name}</div>''')
        return f'''<ul class="list-group">\n{" ".join(lines)}\n</ul>'''

    def enter_room(self, room_id, keeper):
        if keeper.has_room(room_id):
            room = keeper.get_room(room_id)
            # keeper.enter_room(room_id)
            return f'''<div id="messages">Entering room {room}</div>'''
        else:
            return f'''<div id="messages">Trying to enter unknown room {room_id}</div>'''


