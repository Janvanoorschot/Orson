import uuid
import json
import datetime
from datetime import timedelta
import pika.channel
from orson import CHAT_EXCHANGE_NAME, UPDATES_EXCHANGE_NAME, ROOM_ANNOUNCEMENT


class Room:
    id: str
    name: str
    chat_queue_name: str
    connection: pika.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel

    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name
        self.next_t = datetime.datetime.fromtimestamp(-1)
        self.interval = 10

    def init(self, connection, channel):
        self.connection = connection
        self.channel = channel
        # create ingress/egress exchanges for this room
        self.channel.exchange_declare(exchange=CHAT_EXCHANGE_NAME, exchange_type='topic')
        self.channel.exchange_declare(exchange=UPDATES_EXCHANGE_NAME, exchange_type='topic')
        # create queue to the ingress exchange
        queue_result = self.channel.queue_declare('', exclusive=True)
        self.chat_queue_name = queue_result.method.queue
        binding_key = f"{self.name}"
        self.channel.queue_bind(
            exchange=CHAT_EXCHANGE_NAME, queue=self.chat_queue_name, routing_key=binding_key)
        self.channel.basic_consume(
            queue=self.chat_queue_name, on_message_callback=self.chatter, auto_ack=True)

    def chatter(self, ch, method, properties, body):
        pass

    def timer(self, t):
        if self.next_t < t:
            self.next_t = t + timedelta(seconds=24)
            # broadcast your presence
            message = {
                "id": self.id,
                "name": self.name,
                "t": t.isoformat()
            }
            self. channel.basic_publish(
                exchange=UPDATES_EXCHANGE_NAME,
                routing_key=ROOM_ANNOUNCEMENT,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2))
