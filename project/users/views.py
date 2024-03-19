import string
import random
import logging
import requests
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from project.users import users_router
from project.users.models import User
from project.users.schemas import UserBody
from project.database import get_db_session
from project.celery_utils import get_task_info
from project.users.tasks import sample_task, task_process_notification, task_send_welcome_email


logger = logging.getLogger(__name__)
templates = Jinja2Templates('project/users/templates')


def api_call(email: str):
    if random.choice((0, 1)):
        raise Exception('Random processing error')
    requests.post('https://httpbin.org/delay/5')


def random_username():
    username = ''.join([random.choice(string.ascii_lowercase) \
        for _ in range(random.randint(5, 10))])
    return username


@users_router.get('/transaction_celery/')
def transaction_celery(session: Session = Depends(get_db_session)):
    try:
        username = random_username()
        user = User(username=username, email=f'{username}@gmail.com')
        session.add(user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    logger.info('User %s is persistent now', user.id)
    task_send_welcome_email.delay(user.id)
    return {'message': 'done'}


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
