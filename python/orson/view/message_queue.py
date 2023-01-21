import json
import logging
import pika
from orson import CHAT_EXCHANGE_NAME, UPDATES_EXCHANGE_NAME, ROOM_ANNOUNCEMENT


class MessageQueue:
    url: str

    def __init__(self, url="amqp://orson:orson@127.0.0.1:8001/%2F"):
        self.url = url
        connection = pika.BlockingConnection(pika.URLParameters(url=self.url))
        channel = connection.channel()
        exchange = channel.exchange_declare(exchange=CHAT_EXCHANGE_NAME, exchange_type='topic')
        connection.close()

    def send(self, room_name, message):
        connection = pika.BlockingConnection(pika.URLParameters(url=self.url))
        channel = connection.channel()
        body = json.dumps(message, default=str)
        properties = pika.BasicProperties(delivery_mode=2)
        channel.basic_publish(exchange=CHAT_EXCHANGE_NAME, routing_key=room_name, body=body, properties=properties)
        connection.close()
