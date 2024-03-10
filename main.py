import time
from celery import Celery
from project import create_app


app = create_app()

celery = Celery(
    __name__,
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0'
)


@celery.task
def divide(x, y):
    time.sleep(3)
    return x / y
