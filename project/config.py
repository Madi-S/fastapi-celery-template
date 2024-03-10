import os
import pathlib
from functools import lru_cache


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    DATABASE_URL: str = os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR}/db.sqlite3')
    DATABASE_CONNECT_DICT: dict = {}


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_cls_dict = {
        'testing': TestingConfig,
        'production': ProductionConfig,
        'development': DevelopmentConfig
    }
    config_name = os.environ.get('FASTAPI_CONFIG', 'development')
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
