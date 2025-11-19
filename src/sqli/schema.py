from pydantic import BaseModel, Field


class UserLoginSchema(BaseModel):
  __table__ = 'users'
  __op__ = 'select'

  username: str = Field()
  password: str = Field()


class UserInsertSchema(BaseModel):
  __table__ = 'users'
  __op__ = 'insert'

  username: str = Field()
  password: str = Field()
