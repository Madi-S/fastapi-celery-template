import time
from celery import shared_task


@shared_task
def divide(x, y):
    time.sleep(3)
    return x / y
