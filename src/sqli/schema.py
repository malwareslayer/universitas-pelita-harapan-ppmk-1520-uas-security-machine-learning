from pydantic import BaseModel, Field


class UserSearchLoginSchema(BaseModel):
  __table__ = 'users'
  __op__ = 'select'

  username: str = Field()


class UserEmailSearchLoginSchema(BaseModel):
  __table__ = 'users'
  __op__ = 'select'

  email: str = Field(min_length=32, max_length=255)


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
