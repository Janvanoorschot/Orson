from abc import ABC, abstractmethod

class RemoteRoom(ABC):

    @abstractmethod
    def get_room_id(self):
        pass

    def get_room_name(self):
        pass

    @abstractmethod
    def get_clients(self):
        pass

    @abstractmethod
    def client_enter(self, client):
        pass

    @abstractmethod
    def client_leave(self, client):
        pass


class RoomKeeper(ABC):
    rooms: dict = NotImplemented

    @abstractmethod
    def get_room(self, room_id: str) -> RemoteRoom:
        pass

    @abstractmethod
    def has_room(self, room_id: str) -> bool:
        pass

    def get_rooms(self) -> dict:
        pass


class Client(ABC):
    state: int = NotImplemented
    room: RemoteRoom = NotImplemented
    target_room: RemoteRoom = NotImplemented

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def get_client_id(self) -> int:
        pass

    @abstractmethod
    def in_room(self) -> bool:
        pass

    @abstractmethod
    def is_nowhere(self) -> bool:
        pass

    @abstractmethod
    def get_room(self) -> RemoteRoom:
        pass


class ClientManager(ABC):

    @abstractmethod
    def zero_client(self):
        pass

    @abstractmethod
    def create_client(self):
        pass

    @abstractmethod
    def get_client(self, client_id: str):
        pass

    @abstractmethod
    def evt_room_has_lost_client(self, room, client_id):
        pass

    @abstractmethod
    def evt_room_lost(self,  room: RemoteRoom):
        pass

    @abstractmethod
    def enter_room(self, client: Client,  room: RemoteRoom):
        pass

    @abstractmethod
    def leave_room(self, client: Client,  room: RemoteRoom):
        pass


class Caller(ABC):

    @abstractmethod
    def send_message(self, room_id, msg):
        pass
