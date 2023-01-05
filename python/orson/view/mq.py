import pika
import json
from threading import Thread
from orson import CHAT_EXCHANGE_NAME, UPDATES_EXCHANGE_NAME, ROOM_ANNOUNCEMENT


class MessageQueue(object):
    url: str
    connection: pika.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel
    announcement_queue_name: str
    thread: Thread

    def __init__(self, url):
        self.url = url

    def init(self, cb):
        """ Initiase RabbitMQ components """
        self.cb = cb
        parameters = pika.URLParameters(self.url)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        # create ingress/egress exchanges for this room
        self.channel.exchange_declare(exchange=CHAT_EXCHANGE_NAME, exchange_type='topic')
        self.channel.exchange_declare(exchange=UPDATES_EXCHANGE_NAME, exchange_type='topic')
        # create queue to the announcement exchange
        queue_result = self.channel.queue_declare('', exclusive=True)
        self.announcement_queue_name = queue_result.method.queue
        self.channel.queue_bind(
            exchange=UPDATES_EXCHANGE_NAME, queue=self.announcement_queue_name, routing_key=ROOM_ANNOUNCEMENT)
        self.channel.basic_consume(
            queue=self.announcement_queue_name,
            on_message_callback=self.announcement,
            auto_ack=True
        )
        #
        self.thread = Thread(target=self.channel.start_consuming)
        self.thread.start()

    def close(self):
        self.channel.stop_consuming()
        self.channel.cancel()
        self.channel.close()
        self.connection.close()

    def announcement(self, ch, method, properties, body):
        message = json.loads(body)
        self.cb(ROOM_ANNOUNCEMENT, message)





