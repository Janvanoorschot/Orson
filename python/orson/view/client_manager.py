class ClientManager:

    def __init__(self):
        pass

    def create_client(self):
        pass



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

    def __init__(self):
        self.state = STATE_NOWHERE

    def handle_event(self, event):
        pass

    def action_something(self):
        pass