import uuid
import datetime

STATE_NOWHERE = 0
STATE_ROOMSELECTED = 1
STATE_INROOM = 2
STATE_LEAVINGROOM = 3

EVT_SELECTROOM = 0
EVT_ENTERROOM = 1
EVT_LEAVEROOM = 2
EVT_LEFTROOM = 3


class Client:

    state: int
    room: str
    target_room: str

    def __init__(self, client_id):
        self.client_id = client_id
        self.created_at = datetime.datetime.now()
        self.state = STATE_NOWHERE
        self.room = None
        self.target_room = None

    def handle_event(self, event):
        pass

    def action_something(self):
        pass


class ClientManager:

    clients: dict

    def __init__(self):
        self.clients = {}
        self.zero = Client("0")

    def zero_client(self):
        return self.zero

    def create_client(self) -> Client:
        client_id = str(uuid.uuid4())
        self.clients[client_id] = Client(client_id)
        return self.clients[client_id]

