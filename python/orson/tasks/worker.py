# celery  -A orson.tasks.worker worker --loglevel=INFO --without-heartbeat --without-gossip --without-mingle
from celery import Celery
from .config import Default


def make_celery():
    celery = Celery(
        'worker',
        backend="rpc://",
        broker="amqp://orson:orson@127.0.0.1:8001/%2F",
        include=['orson.tasks']
    )
    celery.config_from_object(Default)
    return celery


celery = make_celery()
print("tasks={}".format( celery.tasks.keys()))
