import functools
import logging
import pika
import json
from celery import Task, shared_task
from orson import CHAT_EXCHANGE_NAME


LOGGER = logging.getLogger(__name__)


class PikaPublisher(Task):

    EXCHANGE_TYPE: str = "topic"
    URL: str = "amqp://orson:orson@127.0.0.1:8001/%2F?heartbeat=600&blocked_connection_timeout=300"
    QUEUE_NAME: ""

    def run(self, *args, **kwargs):
        pass

    url: str
    connection: pika.adapters.blocking_connection.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel


    def __init__(self):
        self.connect()

    def close(self):
        if self.channel is not None and self.channel.is_open:
            self.channel.close()
            self.channel = None
        if self.connection is not None and self.connection.is_open:
            self.connection.close()
            self.connection = None

    def connect(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(self.URL))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=CHAT_EXCHANGE_NAME, exchange_type=self.EXCHANGE_TYPE)


@shared_task(name="tasks.publish_message", base=PikaPublisher, bind=True)
def publish_message(self, room_id, message):
    is_send = False
    while not is_send:
        try:
            if self.channel.is_open:
                self.channel.basic_publish(
                    exchange=CHAT_EXCHANGE_NAME,
                    body=json.dumps(message),
                    routing_key=room_id,
                    properties=pika.BasicProperties(content_type='application/json')
                )
                is_send = True
            else:
                self.close()
                self.connect()
        except Exception as sle:
            self.close()
            self.connect()
