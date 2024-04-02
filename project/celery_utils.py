import functools

from celery.result import AsyncResult
from celery.utils.time import get_exponential_backoff_interval
from celery import current_app as current_celery_app, shared_task

from project.config import settings


def create_celery():
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace='CELERY')

    return celery_app


def get_task_info(task_id):
    task = AsyncResult(task_id)
    state = task.state

    if state == 'FAILURE':
        error = str(task.result)
        response = {'state': task.state, 'error': error}
    else:
        response = {'state': task.state}
    return response


class custom_celery_task:

    EXCEPTION_BLOCK_LIST = (
        KeyError,
        TypeError,
        ValueError,
        IndexError,
        UnicodeDecodeError
    )

    def __init__(self, *args, **kwargs):
        self.task_args = args
        self.task_kwargs = kwargs

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            # ... custom code goes here ...
            return func(*args, **kwargs)

        task_func = shared_task(*self.task_args, **self.task_kwargs)(wrapper_func)
        return task_func

    def _get_retry_countdown(self, task_func):
        retry_backoff = int(
            self.task_kwargs.get('retry_backoff', True)
        )

        retry_backoff_max = int(
            self.task_kwargs.get('retry_backoff_max', 600)
        )

        retry_jitter = self.task_kwargs.get(
            'retry_jitter', True
        )

        countdown = get_exponential_backoff_interval(
            factor=retry_backoff,
            full_jitter=retry_jitter,
            maximum=retry_backoff_max,
            retries=task_func.request.retries
        )

        return countdown
