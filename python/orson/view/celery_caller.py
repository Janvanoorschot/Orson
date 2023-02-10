from .iface import Caller


class CeleryCaller(Caller):

    def __init__(self, celery):
        self.celery = celery

    def send_message(self, room_id, msg):
        self.celery.send_task("tasks.publish_message", args=[room_id, msg])
