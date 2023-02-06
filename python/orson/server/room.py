import uuid
import json
import datetime
from dataclasses import dataclass
from datetime import timedelta
import aio_pika
from orson import CHAT_EXCHANGE_NAME, UPDATES_EXCHANGE_NAME, ROOM_ANNOUNCEMENT


@dataclass
class Client:
    client_id: str
    last_seen: datetime


class Room:
    room_id: str
    name: str
    chat_queue_name: str
    connection: aio_pika.connection.AbstractConnection
    channel: aio_pika.channel.AbstractChannel
    chat_exchange: aio_pika.exchange.AbstractExchange
    updates_exchange: aio_pika.exchange.AbstractExchange

    def __init__(self, name):
        self.room_id = str(uuid.uuid4())
        self.name = name
        self.next_t = datetime.datetime.fromtimestamp(-1)
        self.timer_interval = timedelta(seconds=10)
        self.not_seen_interval = timedelta(seconds=20)
        self.clients = {}
        print(f"room[{self.name}]:[{self.room_id}]")

    async def init(self, connection, channel):
        self.connection = connection
        self.channel = channel
        async with self.connection:
            self.chat_exchange = await self.channel.declare_exchange(CHAT_EXCHANGE_NAME, 'topic')
            self.updates_exchange = await self.channel.declare_exchange(UPDATES_EXCHANGE_NAME, 'topic')
            # create queue to the ingress exchange
            queue = await self.channel.declare_queue('', exclusive=True)
            self.chat_queue_name = queue.name
            binding_key = f"{self.room_id}"
            await queue.bind(self.chat_exchange, binding_key)
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        body = message.body.decode('UTF-8')
                        msg = json.loads(body)
                        await self.chatter(msg)

    async def chatter(self, msg):
        cmd = msg['msg']
        if cmd == 'enter':
            client_id = msg['client_id']
            if client_id not in self.clients:
                self.client_enter(client_id)
        elif cmd == 'leave':
            client_id = msg['client_id']
            if client_id in self.clients:
                self.client_leave(self.clients[client_id])
        elif cmd == 'update':
            self.clients_update(msg['client_ids'])
        else:
            pass

    def client_enter(self, client_id: str):
        client = Client(client_id, datetime.datetime.now())
        self.clients[client_id] = client

    def client_leave(self, client: Client):
        del self.clients[client.client_id]

    def clients_update(self, client_ids):
        # update our client-list with the client-list send by (one of the) server(s)
        now = datetime.datetime.now()
        for client_id in client_ids:
            if client_id in self.clients:
                client = self.clients[client_id]
                client.last_seen = now
            else:
                # implicit 'enter'
                self.client_enter(client_id)
        # check if we have not heard from clients for to long
        for client_id, client in self.clients.items():
            last_seen = now - client.last_seen
            if last_seen > self.not_seen_interval:
                # implicit 'leave'
                self.client_leave(client)

    def clients_dump(self):
        t = f'{datetime.datetime.now():%Y-%m-%d %H:%M:%S%z}'
        r = self.room_id
        cs = '/'.join([client_id for client_id in self.clients.keys()])
        print(f'[{t}][{r}][{cs}]')

    async def timer(self, t):
        if self.next_t < t:
            self.next_t = t + self.timer_interval
            # announce your presence
            message = {
                "id": self.room_id,
                "name": self.name,
                "t": t.isoformat(),
                "clients": [client_id for client_id in self.clients.keys()]
            }
            await self.updates_exchange.publish(
                aio_pika.Message(body=json.dumps(message).encode()),
                routing_key=ROOM_ANNOUNCEMENT
            )
            self.clients_dump()
