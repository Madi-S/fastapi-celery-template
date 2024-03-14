import time
import random
import logging
import requests
from celery import shared_task
from celery.contrib import rdb


logger = logging.getLogger(__name__)

@shared_task
def divide(x: int, y: int) -> float:
    # rdb.set_trace()
    time.sleep(3)
    return x / y


@shared_task()
def sample_task(email: str) -> None:
    from project.users.views import api_call
    api_call(email)


@shared_task(bind=True)
def task_process_notification(self):
    try:
        if not random.choice((0, 1)):
            raise Exception()
        requests.post('https://httpbin.org/delay/5')
    except Exception as e:
        logger.error('exception raised, it would be retry after 5 seconds')
        raise self.retry(exc=e, countdown=5)