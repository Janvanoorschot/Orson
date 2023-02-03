from . import Client


class ClientSession:
    """ Client state information maintained with each session
    """
    client: Client

    def __init__(self, client):
        self.client = client

