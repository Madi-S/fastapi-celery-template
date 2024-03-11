import time
from celery import Celery
from project import create_app


app = create_app()
celery = app.celery_app
