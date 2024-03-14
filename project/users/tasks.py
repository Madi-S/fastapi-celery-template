import time
import random
import requests
from asgiref.sync import async_to_sync

from celery import shared_task
from celery.signals import task_postrun
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task
def divide(x: int, y: int) -> float:
    # from celery.contrib import rdb
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


@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    from project.ws.views import update_celery_task_status
    async_to_sync(update_celery_task_status)(task_id)
