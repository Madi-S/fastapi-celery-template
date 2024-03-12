import time
from celery import shared_task
from celery.contrib import rdb


@shared_task
def divide(x, y):
    # rdb.set_trace()
    time.sleep(3)
    return x / y
