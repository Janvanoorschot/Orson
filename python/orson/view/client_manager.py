import uuid
import datetime
from queue import Queue
from flask import render_template, current_app
from orson.view import websockets
from orson.view import keeper
from . import RemoteRoom, Client, ClientManager, Caller


STATE_NOWHERE = 0
STATE_ROOMSELECTED = 1
STATE_INROOM = 2
STATE_LEAVINGROOM = 3

EVT_REST_EnterRoom = 0
EVT_REST_LeaveRoom = 1
EVT_Alert_EnteredRoom = 2
EVT_Alert_LeftRoom = 3
EVT_Alert_RoomDisappeared = 4


class ClientImpl(Client):

    client_id: str
    name: str
    created_at: datetime
    state: int
    room: RemoteRoom
    target_room: RemoteRoom

    def __init__(self, client_id, name):
        self.client_id = client_id
        self.name = name
        self.created_at = datetime.datetime.now()
        self.reset()

    def get_client_id(self):
        return self.client_id

    def in_room(self):
        return self.state == STATE_INROOM

    def is_nowhere(self):
        return self.state == STATE_NOWHERE

    def get_room(self):
        return self.room

    def reset(self):
        self.state = STATE_NOWHERE
        self.room = None
        self.target_room = None


class ClientManagerImpl(ClientManager):

    caller: Caller
    clients: dict

    def __init__(self, caller: Caller):
        self.caller = caller
        self.clients = {}
        self.zero = ClientImpl("0", "client_0")

    def has_client(self, client_id) -> bool:
        return client_id in self.clients

    def get_client(self, client_id) -> Client:
        return self.clients.get(client_id, None)

    def zero_client(self) -> Client:
        return self.zero

    def create_client(self, client_id=str(uuid.uuid4())) -> Client:
        client_name = f"client[{len(self.clients)}]"
        self.clients[client_id] = ClientImpl(client_id, client_name)
        return self.clients[client_id]

    def event(self, evt: int, client: Client, *args):
        """ Simple state machine handling client movements"""
        if client.state == STATE_NOWHERE:
            if evt == EVT_REST_EnterRoom:
                """ entering a room """
                room = args[0]
                client.state = STATE_ROOMSELECTED
                client.room = None
                client.target_room = room
        elif client.state == STATE_ROOMSELECTED:
            if evt == EVT_Alert_EnteredRoom:
                """ now in room """
                room = args[0]
                client.state = STATE_INROOM
                client.room = room
                client.target_room = None
                room.client_enter(client)
                self.inform_clients()
        elif client.state == STATE_INROOM:
            if evt == EVT_REST_LeaveRoom:
                """ leaving room """
                client.state = STATE_LEAVINGROOM
                client.target_room = None
            elif evt == EVT_Alert_LeftRoom:
                """ unexpected sudden departure (room gone?) """
                room = args[0]
                client.state = STATE_NOWHERE
                client.room = None
                client.target_room = None
                room.client_leave(client)
                self.inform_clients()
        elif client.state == STATE_LEAVINGROOM:
            if evt == EVT_Alert_LeftRoom:
                """ left  room """
                room = args[0]
                client.state = STATE_NOWHERE
                client.room = None
                client.target_room = None
                room.client_leave(client)
                self.inform_clients()

    def inform_clients(self):
        html_blob = self.format_announcement()
        for ws, content in websockets.items():
            queue: Queue = content[0]
            queue.put(html_blob)

    def format_announcement(self) -> str:
        # send the complete rooms/clients matrix back
        m = {
            'rooms': keeper.rooms
        }
        return render_template("rooms_matrix.html", **m)


    ######################################################################################
    # Event functions called by other entities
    def evt_room_has_new_client(self, room, client_id):
        # the client has entered the room
        if self.get_client(client_id):
            self.event(EVT_Alert_EnteredRoom, self.get_client(client_id), room)

    def evt_room_has_lost_client(self, room, client_id):
        # the client has left the room
        if self.get_client(client_id):
            self.event(EVT_Alert_LeftRoom, self.get_client(client_id), room)

    def evt_room_lost(self, room):
        # a room has been blasted from space
        for client_id, client in self.clients.items():
            if client.room == room:
                self.event(EVT_Alert_LeftRoom, self.get_client(client_id), room)
            if client.room == room or client.target_room == room:
                client.reset()

    def enter_room(self, client: Client, room: RemoteRoom):
        # client requests to enter a room
        self.event(EVT_REST_EnterRoom, client, room)
        # send an 'enter' message to the room
        msg = {
            'msg': 'enter',
            'client_id': client.get_client_id()
        }
        self.caller.send_message(room.get_room_id(), msg)

    def leave_room(self, client: Client):
        # client requests to leave a room
        if client.in_room():
            # send a 'leave' message to the room
            msg = {
                'msg': 'leave',
                'client_id': client.get_client_id()
            }
            self.caller.send_message(client.get_room().get_room_id(), msg)
            # update local state
            self.event(EVT_REST_LeaveRoom, client)

