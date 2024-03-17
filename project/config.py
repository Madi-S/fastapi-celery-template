import os
import pathlib
from kombu import Queue
from functools import lru_cache


def route_task(name, args, kwargs, options, task=None, **kw):
    if ':' in name:
        queue, _ = name.split(':')
        return {'queue': queue}
    return {'queue': 'default'}


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent

    DATABASE_URL: str = os.environ.get(
        'DATABASE_URL', f'sqlite:///{BASE_DIR}/db.sqlite3')
    DATABASE_CONNECT_DICT: dict = {}

    WS_MESSAGE_QUEUE: str = os.environ.get(
        'WS_MESSAGE_QUEUE', 'redis://127.0.0.1:6379/0')

    CELERY_BROKER_URL: str = os.environ.get(
        'CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
    CELERY_RESULT_BACKEND: str = os.environ.get(
        'CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')

    CELERY_BEAT_SCHEDULE: dict = {
        'task-schedule-work': {
            'task': 'task_schedule_work',
            'schedule': 200.0  # every 200 seconds
            # this supports crontab, timedeleta and solar formats
        }
    }

    CELERY_TASK_DEFAULT_QUEUE: str = 'default'

    CELERY_TASK_CREATE_MISSING_QUEUES: bool = False

    CELERY_TASK_QUEUES: tuple = (
        Queue('default'),
        Queue('high_priority'),
        Queue('low_priority')
    )

    # CELERY_TASK_ROUTES: dict = {
    #     'project.users.tasks.*': {
    #         'queue': 'high_priority'
    #     }
    # }
    CELERY_TASK_ROUTES: tuple = (route_task, )


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


@lru_cache()
def get_settings() -> BaseConfig:
    config_cls_dict = {
        'testing': TestingConfig,
        'production': ProductionConfig,
        'development': DevelopmentConfig
    }
    config_name = os.environ.get('FASTAPI_CONFIG', 'development')
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
