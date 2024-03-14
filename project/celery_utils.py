from celery.result import AsyncResult
from celery import current_app as current_celery_app

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
