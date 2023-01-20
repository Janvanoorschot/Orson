import asyncio
import json
import logging
import aio_pika
from orson import CHAT_EXCHANGE_NAME, UPDATES_EXCHANGE_NAME, ROOM_ANNOUNCEMENT


class MessageQueue:
    url: str
    connection: aio_pika.connection.AbstractConnection
    channel: aio_pika.channel.AbstractChannel
    exchange: aio_pika.exchange.AbstractExchange

    def __init__(self, url="amqp://orson:orson@127.0.0.1:8001/%2F"):
        self.url = url
        self.loop = None

    def send(self, room_name, message):
        if self.loop is None:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.a_send(room_name, message))

    async def a_send(self, room_name, message):
        connection = await aio_pika.connect_robust(self.url)
        channel = await connection.channel()
        exchange = await channel.declare_exchange(CHAT_EXCHANGE_NAME, 'topic')
        await exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=room_name
        )
        await connection.close()
