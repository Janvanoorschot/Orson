import functools
import logging
import pika
from celery import Task, shared_task
from orson import CHAT_EXCHANGE_NAME, UPDATES_EXCHANGE_NAME, ROOM_ANNOUNCEMENT


LOGGER = logging.getLogger(__name__)


class CBPikaPublisher(Task):

    EXCHANGE_TYPE: str = "topic"
    URL: str = "amqp://orson:orson@127.0.0.1:8001/%2F"
    QUEUE_NAME: ""

    def run(self, *args, **kwargs):
        pass

    url: str
    connection: pika.SelectConnection
    channel: pika.spec.Channel

    def __init__(self):
        self.connect()

    def connect(self):
        return pika.SelectConnection(
            pika.URLParameters(self.URL),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed
        )

    def on_connection_open(self, _unused_connection):
        self.open_channel()

    def on_connection_open_error(self, connection, err):
        LOGGER(f"connection open failed: {str(err)}")

    def on_connection_closed(self, connection, reason):
        self.channel = None

    def open_channel(self):
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        self.channel.add_on_close_callback(self.on_channel_closed)
        self.setup_exchange(CHAT_EXCHANGE_NAME)

    def on_channel_close(self, channel, reason):
        self.channel = None

    def setup_exchange(self, exchange_name):
        cb = functools.partial(
            self.on_exchange_declareok,
            userdata=exchange_name
        )
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=self.EXCHANGE_TYPE,
            callback=cb
        )

    def on_exchange_declareok(self, frame, userdata):
        self.setup_queue(self.QUEUE_NAME)

    def setup_queue(self, queue_name):
        self.channel.queue_declare(
            queue=queue_name,
            callback=self.on_queue_declareok
        )

    def on_queue_declareok(self, frame):
        self.channel.queue_bind(
            self.QUEUE_NAME,
            self.EXCHANGE_NAME,
            routing_key=self.ROUTING_KEY,
            callback=self.on_bindok
        )

    def on_bindok(self, frame):
        # self.channel.confirm_delivery(self.on_delivery_confirmation)
        pass



@shared_task(name="tasks.publish_message", base=CBPikaPublisher, bind=True)
def cb_publish_message(self, message):
    pass
