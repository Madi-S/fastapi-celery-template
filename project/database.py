from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from project.config import settings


# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-sqlalchemy-engine
engine = create_engine(
    settings.DATABASE_URL, connect_args=settings.DATABASE_CONNECT_DICT
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
