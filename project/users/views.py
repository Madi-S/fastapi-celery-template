import random
import logging
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from project.users import users_router
from project.users.schemas import UserBody
from project.celery_utils import get_task_info
from project.users.tasks import sample_task, task_process_notification


logger = logging.getLogger(__name__)
templates = Jinja2Templates('project/users/templates')


def api_call(email: str):
    if random.choice((0, 1)):
        raise Exception('Random processing error')
    requests.post('https://httpbin.org/delay/5')


@users_router.get('/form/')
def form_example_get(request: Request):
    return templates.TemplateResponse('form.html', {'request': request})


@users_router.post('/form/')
def form_example_post(user_body: UserBody):
    task = sample_task.delay(user_body.email)
    return JSONResponse({'task_id': task.task_id})


@users_router.get('/task_status/')
def task_status(task_id: str):
    response = get_task_info(task_id)
    return JSONResponse(response)


@users_router.post('/webhook_test_sync/')
def webhook_test_sync():
    if not random.choice((0, 1)):
        raise Exception()
    requests.post('https://httpbin.org/delay/5')
    return 'pong'


@users_router.post('/webhook_test_async/')
def webhook_test_async():
    task = task_process_notification.delay()
    logger.debug('Task id: %s', task.id)
    return 'pong'


@users_router.get('/form_ws/')
def form_ws_example(request: Request):
    return templates.TemplateResponse('form_ws.html', {'request': request})


@users_router.get('/form_socketio')
def form_socketio_example(request: Request):
    return templates.TemplateResponse('form_socketio.html', {'request': request})
