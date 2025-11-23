from sqlalchemy import (
  Column,
  Float,
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
  error = Column(Integer)
  created = Column(Text, server_default=text('CURRENT_TIMESTAMP'))

  # relationships
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
  payload = Column(
    Integer,
    ForeignKey('payloads.id', ondelete='CASCADE'),
    nullable=False,
  )

  serde = Column(Text)

  # Parse Tree Metrics
  nodes = Column(Integer)
  leafs = Column(Integer)
  trees = Column(Integer)
  subtrees = Column(Integer)

  # Query Metrics
  subqueries = Column(Integer)
  selects = Column(Integer)
  inserts = Column(Integer)
  updates = Column(Integer)
  deletes = Column(Integer)
  creates = Column(Integer)
  drops = Column(Integer)
  alters = Column(Integer)
  wheres = Column(Integer)
  havings = Column(Integer)
  ins = Column(Integer)

  # Set Operations Metrics
  unions = Column(Integer)
  intersects = Column(Integer)
  excepts = Column(Integer)
  joins = Column(Integer)

  # Clause Metrics
  limits = Column(Integer)
  offsets = Column(Integer)
  orders = Column(Integer)
  groups = Column(Integer)

  # CTE Metrics
  ctes = Column(Integer)
  withs = Column(Integer)

  # Literal Metrics
  literals = Column(Integer)
  literal_length = Column(Integer)
  literal_digits = Column(Integer)
  literal_letters = Column(Integer)
  literal_uppers = Column(Integer)
  literal_lowers = Column(Integer)
  literal_whitespaces = Column(Integer)
  literal_specials = Column(Integer)
  literal_equals = Column(Integer)
  literal_single_quotes = Column(Integer)
  literal_double_quotes = Column(Integer)
  literal_dashes = Column(Integer)
  literal_slashes = Column(Integer)
  literal_stars = Column(Integer)
  literal_semicolons = Column(Integer)
  literal_percents = Column(Integer)
  literal_parentheses = Column(Integer)
  literal_commas = Column(Integer)
  literal_dots = Column(Integer)
  literal_underscores = Column(Integer)
  literal_repeats = Column(Integer)
  literal_imbalances = Column(Integer)

  # Atomic Metrics
  identifiers = Column(Integer)

  # Binaries Metrics
  binaries = Column(Integer)
  bitors = Column(Integer)
  bitands = Column(Integer)
  bitxors = Column(Integer)

  # Arithmetic Metrics
  arithmetics = Column(Integer)
  additions = Column(Integer)
  subtractions = Column(Integer)
  multiplications = Column(Integer)
  divisions = Column(Integer)
  modulos = Column(Integer)

  # Conditions Metrics
  conditions = Column(Integer)
  eqs = Column(Integer)
  neqs = Column(Integer)
  gts = Column(Integer)
  lts = Column(Integer)
  gtes = Column(Integer)
  ltes = Column(Integer)
  betweens = Column(Integer)
  cases = Column(Integer)

  # Predicates Metrics
  predicates = Column(Integer)
  ors = Column(Integer)
  ands = Column(Integer)
  nots = Column(Integer)

  # Other Metrics
  functions = Column(Integer)
  comments = Column(Integer)

  payload_obj = relationship('Payload', back_populates='asts')


class Lexical(__base__):
  __tablename__ = 'lexicals'

  id = Column(Integer, primary_key=True, autoincrement=True)
  payload = Column(
    Integer,
    ForeignKey('payloads.id', ondelete='CASCADE'),
    nullable=False,
  )

  # Basic counts
  length = Column(Integer)
  digits = Column(Integer)
  ratio_digits = Column(Float)
  letters = Column(Integer)
  ratio_letters = Column(Float)
  uppers = Column(Integer)
  ratio_upper = Column(Float)
  lowers = Column(Integer)
  ratio_lower = Column(Float)
  whitespaces = Column(Integer)
  ratio_whitespace = Column(Float)
  specials = Column(Integer)
  ratio_special = Column(Float)
  shannon = Column(Float)

  # Special Character Counts
  equals = Column(Integer)
  single_quotes = Column(Integer)
  double_quotes = Column(Integer)
  dashes = Column(Integer)
  slashes = Column(Integer)
  stars = Column(Integer)
  semicolons = Column(Integer)
  percents = Column(Integer)
  parentheses = Column(Integer)
  commas = Column(Integer)
  dots = Column(Integer)
  underscores = Column(Integer)

  # Shape / Structural Weirdness
  repeats = Column(Integer)
  imbalances = Column(Integer)

  # Reserved Keywords
  ors = Column(Integer)
  ands = Column(Integer)
  unions = Column(Integer)
  selects = Column(Integer)
  inserts = Column(Integer)
  updates = Column(Integer)
  deletes = Column(Integer)
  drops = Column(Integer)
  sleeps = Column(Integer)
  comments = Column(Integer)

  payload_obj = relationship('Payload', back_populates='lexicals')


__all__ = ['__base__', 'Payload', 'AST', 'Lexical']
