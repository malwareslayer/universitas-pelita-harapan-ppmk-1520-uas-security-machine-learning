import sqlite3
from pathlib import Path

SCHEMA_PATH = (Path(__file__).resolve().parent / 'db' / 'schema.sql').resolve()
SCHEMA_VERSION = 0


def initialize(path: Path):
  location = path.resolve()

  if location.exists() or location.is_dir():
    raise FileExistsError(f'Database file already exists at {str(location)}')

  connection = sqlite3.connect(str(path.resolve()))

  try:
    with open(SCHEMA_PATH) as f:
      connection.executescript(f.read())

    connection.commit()
  except (sqlite3.OperationalError, sqlite3.DatabaseError):
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


__all__ = ['initialize', 'check']
