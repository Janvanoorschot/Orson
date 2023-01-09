import uuid
import json
import datetime
from datetime import timedelta
import aio_pika
import httpx
from orson import UPDATES_EXCHANGE_NAME, ROOM_ANNOUNCEMENT


class Alert:
    id: str
    url: str
    chat_queue_name: str
    connection: aio_pika.connection.AbstractConnection
    channel: aio_pika.channel.AbstractChannel
    updates_exchange: aio_pika.exchange.AbstractExchange

    def __init__(self, url):
        self.id = str(uuid.uuid4())
        self.url = url
        self.next_t = datetime.datetime.fromtimestamp(-1)
        self.interval = 10

    async def init(self, connection: aio_pika.connection.AbstractConnection, channel: aio_pika.channel.AbstractChannel):
        self.connection = connection
        self.channel = channel
        # create ingress/egress exchanges for this room
        self.updates_exchange = await self.channel.declare_exchange(UPDATES_EXCHANGE_NAME, 'topic')
        # create queue to the ingress exchange
        queue = await self.channel.declare_queue('', exclusive=True)
        self.chat_queue_name = queue.name
        binding_key = ROOM_ANNOUNCEMENT
        await queue.bind(self.updates_exchange, binding_key)
        await queue.consume(self.updates, no_ack=True)

    async def updates(self, pika_message: aio_pika.abc.AbstractIncomingMessage,) -> None:
        try:
            # pass it on to our Flask web presence (could add some intelligence?)
            message = json.loads(pika_message.body)
            httpx.post(self.url, json=message)
        except Exception as e:
            # error occurred, pass it on
            pass

    async def timer(self, t):
        if self.next_t < t:
            self.next_t = t + timedelta(seconds=self.interval)
            # do something timely
