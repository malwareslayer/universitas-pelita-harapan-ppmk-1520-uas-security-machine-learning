import faker
from sqlalchemy import Integer, String

from parser.types import Base, FakeColumn


class User(Base):
  __tablename__ = 'user'
  __faker__ = faker.Faker()

  id = FakeColumn(Integer(), primary_key=True, autoincrement=True)
  username = FakeColumn(String(), faker=__faker__, pattern='user_name', unique=True)
  email = FakeColumn(String(), faker=__faker__, pattern='email', unique=True)


__all__ = ['Base', 'User']
