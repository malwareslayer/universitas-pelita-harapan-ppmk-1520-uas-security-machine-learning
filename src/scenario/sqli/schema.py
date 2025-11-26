import faker
from parser import Base, FakeColumn
from sqlalchemy import Integer, String


class User(Base):
  __tablename__ = 'user'
  __faker__ = faker.Faker()

  id = FakeColumn(Integer(), primary_key=True, autoincrement=True)
  name = FakeColumn(String(), pattern='name', nullable=False)
  username = FakeColumn(String(), pattern='user_name', nullable=False, unique=True)
  email = FakeColumn(String(), pattern=['email', 'company_email'], nullable=False, unique=True)


__all__ = ['Base', 'User']
