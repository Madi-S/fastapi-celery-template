import os
import pathlib
from functools import lru_cache


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent

    DATABASE_URL: str = os.environ.get(
        'DATABASE_URL', f'sqlite:///{BASE_DIR}/db.sqlite3')
    DATABASE_CONNECT_DICT: dict = {}

    CELERY_BROKER_URL: str = os.environ.get(
        'CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
    CELERY_RESULT_BACKEND: str = os.environ.get(
        'CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')

    WS_MESSAGE_QUEUE: str = os.environ.get(
        'WS_MESSAGE_QUEUE', 'redis://127.0.0.1:6379/0')

    CELERY_BEAT_SCHEDULE: dict = {
        'task-schedule-work': {
            'task': 'task_schedule_work',
            'schedule': 5.0  # every five seconds
            # this supports crontab, timedeleta and solar formats
        }
    }


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
