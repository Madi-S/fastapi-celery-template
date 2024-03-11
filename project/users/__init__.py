from fastapi import APIRouter


users_router = APIRouter(prefix='/users')

from . import models, tasks  # noqa
