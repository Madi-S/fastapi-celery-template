import factory

from project.users.models import User
from project.database import SessionLocal


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = SessionLocal()
        sqlalchemy_get_or_create = ('username',)
        sqlalchemy_session_persistence = 'commit'
    username = factory.Faker('user_name')

    email = factory.LazyAttribute(lambda o: '%s@example.com' % o.username)
