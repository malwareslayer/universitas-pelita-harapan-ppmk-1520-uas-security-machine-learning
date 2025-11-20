import sqlite3
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import faker
import requests

SCHEMA_VERSION = 0


def initialize(path: Path):
  location = path.resolve()

  if location.exists() or location.is_dir():
    raise FileExistsError(f'Database file already exists at {str(location)}')

  connection = sqlite3.connect(str(path.resolve()))

  try:
    with open(path) as f:
      connection.executescript(f.read())

    connection.commit()
  except (sqlite3.OperationalError, sqlite3.DatabaseError, FileNotFoundError):
    raise sqlite3.OperationalError('Failed to initialize database') from sqlite3.DatabaseError

  print('Database initialized successfully')

  return connection


def check(path: Path):
  if not path.exists():
    raise FileNotFoundError(f'Database file not found at {str(path.resolve())}')

  try:
    connection = sqlite3.connect(str(path), check_same_thread=False)
  except sqlite3.Error:
    raise sqlite3.Error('Failed to open database') from sqlite3.Error

  try:
    cursor = connection.cursor()
    cursor.execute('PRAGMA user_version;')

    row = cursor.fetchone()
    version = row[0] if row else 0

    if version != SCHEMA_VERSION:
      raise sqlite3.DatabaseError(f'Database schema version mismatch: expected {SCHEMA_VERSION}, got {version}')

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    missing = {'payloads', 'asts', 'lexicals'} - tables

    if missing:
      raise sqlite3.DatabaseError(f'Database schema is missing tables: {", ".join(missing)}')
  except (sqlite3.Error, sqlite3.DatabaseError):
    raise sqlite3.DatabaseError('Failed to verify database schema') from sqlite3.Error

  return connection


def generate(url: str, name: str, count: int, schema: Path):
  if not schema.exists():
    raise FileNotFoundError('Schema file not found')

  spec = spec_from_file_location('schema', str(schema))
  module = module_from_spec(spec)

  spec.loader.exec_module(module)

  try:
    cls = getattr(module, name)
  except AttributeError:
    raise AttributeError(f'Pydantic schema {name} not found in {str(schema)}') from AttributeError

  fields = cls.model_fields

  fake = faker.Faker()

  mapping = {
    str: fake.word,
    int: fake.random_int,
    float: fake.pyfloat,
    bool: fake.pybool,
  }

  data = []

  for _ in range(count + 1):
    data.append({f: mapping[t.annotation]() for f, t in fields.items() if t.annotation in mapping})

  for json in data:
    response = requests.post(f'{url}/{name}', json=json)

    if response.status_code != 200:
      raise ConnectionError(f'Failed to send data to {url}: {response.status_code}')


__all__ = ['initialize', 'check', 'generate']
