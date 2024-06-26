import time
import random
import requests
from asgiref.sync import async_to_sync

from celery import Task, shared_task
from celery.signals import task_postrun
from celery.utils.log import get_task_logger

from project.database import db_context
from project.celery_utils import custom_celery_task


logger = get_task_logger(__name__)


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception, KeyError)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True


@shared_task(bind=True)
def task_add_subscription(self, user_pk):
    with db_context() as session:
        try:
            from project.users.models import User

            user = session.query(User).get(user_pk)
            requests.post('https://httpbin.org/delay/5',
                          data={'email': user.email})
        except Exception as e:
            raise self.retry(exc=e)


@shared_task(name='task_schedule_work')
def task_schedule_work():
    logger.info('task_schedule_work run')


@shared_task(name='default:dynamic_example_one')
def dynamic_example_one():
    logger.info('Example one')


@shared_task(name='low_priority:dynamic_example_two')
def dynamic_example_two():
    logger.info('Example two')


@shared_task(name='high_priority:dynamic_example_three')
def dynamic_example_three():
    logger.info('Example three')


@shared_task
def divide(x: int, y: int) -> float:
    # from celery.contrib import rdb
    # rdb.set_trace()
    time.sleep(3)
    return x / y


@shared_task
def task_send_welcome_email(user_pk):
    from project.users.models import User

    with db_context() as session:
        user = session.query(User).get(user_pk)
        logger.info('Sent email to %s %s', user.email, user.id)


@shared_task()
def sample_task(email: str) -> None:
    from project.users.views import api_call
    api_call(email)


# @shared_task(bind=True, base=BaseTaskWithRetry)
@custom_celery_task(max_retires=3)
def task_process_notification(self):
    if not random.choice((0, 1)):
        raise Exception()
    requests.post('https://httpbin.org/delay/5')


@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    from project.ws.views import update_celery_task_status
    async_to_sync(update_celery_task_status)(task_id)

    from project.ws.views import update_celery_task_status_socketio
    update_celery_task_status_socketio(task_id)
