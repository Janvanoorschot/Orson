from celery import Task, shared_task


class SomeTask(Task):

    def __init__(self):
        self.eikel = 42

    def run(self):
        pass


@shared_task(name='tasks.add_together', base=SomeTask, bind=True)
def add_together(self, x, y):
    return x + y + self.eikel

