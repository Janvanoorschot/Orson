import json
import logging
import aio_pika
from orson import CHAT_EXCHANGE_NAME, UPDATES_EXCHANGE_NAME, ROOM_ANNOUNCEMENT

class MessageQueue:
    url: str
    connection: aio_pika.connection.AbstractConnection
    channel: aio_pika.channel.AbstractChannel
    exchange: aio_pika.exchange.AbstractExchange

    def __init__(self, url="amqp://orson:orson@127.0.0.1:8001/%2F", exchange_name=""):
        self.url = url

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(CHAT_EXCHANGE_NAME, 'topic')

    async def send(self, room_name, message):
        await self.exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=room_name
        )



