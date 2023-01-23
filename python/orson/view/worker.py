from celery import Celery


def make_celery():
    celery = Celery(
        'worker',
        backend="rpc://",
        broker="amqp://orson:orson@127.0.0.1:8001/%2F",
        include=['orson.tasks']
    )
    return celery


celery = make_celery()
print("tasks={}".format( celery.tasks.keys()))
