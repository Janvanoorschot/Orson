from celery import shared_task


@shared_task(name='tasks.add_together')
def add_together(x, y):
    return x + y

