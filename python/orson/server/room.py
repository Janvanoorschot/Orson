import uuid
import json
import datetime
from datetime import timedelta
import aio_pika
from orson import CHAT_EXCHANGE_NAME, UPDATES_EXCHANGE_NAME, ROOM_ANNOUNCEMENT


class Room:
    id: str
    name: str
    chat_queue_name: str
    connection: aio_pika.connection.AbstractConnection
    channel: aio_pika.channel.AbstractChannel
    chat_exchange: aio_pika.exchange.AbstractExchange
    updates_exchange: aio_pika.exchange.AbstractExchange

    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.next_t = datetime.datetime.fromtimestamp(-1)
        self.interval = 10

    async def init(self, connection, channel):
        self.connection = connection
        self.channel = channel
        # create ingress/egress exchanges for this room
        self.chat_exchange = await self.channel.declare_exchange(CHAT_EXCHANGE_NAME, 'topic')
        self.updates_exchange = await self.channel.declare_exchange(UPDATES_EXCHANGE_NAME, 'topic')
        # create queue to the ingress exchange
        queue = await self.channel.declare_queue('', exclusive=True)
        self.chat_queue_name = queue.name
        binding_key = f"{self.name}"
        await queue.bind(self.chat_exchange, binding_key)
        await queue.consume(self.chatter, no_ack=True)

    async def chatter(self, ch, method, properties, body):
        pass

    async def timer(self, t):
        if self.next_t < t:
            self.next_t = t + timedelta(seconds=24)
            # broadcast your presence
            message = {
                "id": self.id,
                "name": self.name,
                "t": t.isoformat()
            }
            await self.updates_exchange.publish(
                aio_pika.Message(body=json.dumps(message).encode()),
                routing_key=ROOM_ANNOUNCEMENT
            )
