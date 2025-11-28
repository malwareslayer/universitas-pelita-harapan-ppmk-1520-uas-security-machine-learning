from sqlalchemy import (
  Column,
  ForeignKey,
  Integer,
  Text,
  text,
)
from sqlalchemy.orm import declarative_base, relationship

__base__ = declarative_base()


class Payload(__base__):
  __tablename__ = 'payloads'

  id = Column(Integer, primary_key=True, autoincrement=True)
  payload = Column(Text, nullable=False, unique=True)
  dialect = Column(Text)
  label = Column(Integer)
  created = Column(Text, server_default=text('CURRENT_TIMESTAMP'))

  asts = relationship(
    'AST',
    back_populates='payload',
    cascade='all, delete-orphan',
  )
  lexicals = relationship(
    'Lexical',
    back_populates='payload',
    cascade='all, delete-orphan',
  )


class AST(__base__):
  __tablename__ = 'asts'

  id = Column(Integer, primary_key=True, autoincrement=True)
  payload_id = Column(
    Integer,
    ForeignKey('payloads.id', ondelete='CASCADE'),
    nullable=False,
  )

  serde = Column(Text)

  node = Column(Integer)
  leaf = Column(Integer)

  subquery = Column(Integer)
  select = Column(Integer)
  _from = Column(Integer, name='from')
  insert = Column(Integer)
  update = Column(Integer)
  delete = Column(Integer)
  create = Column(Integer)
  drop = Column(Integer)
  alter = Column(Integer)
  where = Column(Integer)
  having = Column(Integer)
  _in = Column(Integer, name='in')

  union = Column(Integer)
  intersect = Column(Integer)
  _except = Column(Integer, name='except')
  join = Column(Integer)

  limit = Column(Integer)
  offset = Column(Integer)
  order = Column(Integer)
  group = Column(Integer)

  cte = Column(Integer)
  _with = Column(Integer, name='with')

  literal = Column(Integer)
  string = Column(Integer)
  number = Column(Integer)

  identifier = Column(Integer)

  star = Column(Integer)
  null = Column(Integer)
  dpipe = Column(Integer)

  binary = Column(Integer)

  add = Column(Integer)
  sub = Column(Integer)
  mul = Column(Integer)
  div = Column(Integer)
  mod = Column(Integer)

  condition = Column(Integer)
  eq = Column(Integer)
  neq = Column(Integer)
  gt = Column(Integer)
  gte = Column(Integer)
  lt = Column(Integer)
  lte = Column(Integer)
  between = Column(Integer)
  case = Column(Integer)
  like = Column(Integer)

  predicate = Column(Integer)
  _or = Column(Integer, name='or')
  _and = Column(Integer, name='and')
  _not = Column(Integer, name='not')

  bitwiseor = Column(Integer)
  bitwiseand = Column(Integer)
  bitwisexor = Column(Integer)

  func = Column(Integer)
  comment = Column(Integer)

  payload = relationship('Payload', back_populates='asts')


class Lexical(__base__):
  __tablename__ = 'lexicals'

  id = Column(Integer, primary_key=True, autoincrement=True)
  payload_id = Column(
    Integer,
    ForeignKey('payloads.id', ondelete='CASCADE'),
    nullable=False,
  )

  length = Column(Integer)
  digit = Column(Integer)
  letter = Column(Integer)
  upper = Column(Integer)
  lower = Column(Integer)
  whitespace = Column(Integer)
  punctuation = Column(Integer)
  comment = Column(Integer)

  equal = Column(Integer)
  single = Column(Integer)
  double = Column(Integer)
  dash = Column(Integer)
  pipe = Column(Integer)
  slash = Column(Integer)
  star = Column(Integer)
  semicolon = Column(Integer)
  percent = Column(Integer)
  parentheses = Column(Integer)
  comma = Column(Integer)

  payload = relationship('Payload', back_populates='lexicals')


__all__ = ['__base__', 'Payload', 'AST', 'Lexical']
