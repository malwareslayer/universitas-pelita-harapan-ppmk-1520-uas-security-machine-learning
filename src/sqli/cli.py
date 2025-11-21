import argparse
import threading
from collections.abc import Sequence
from pathlib import Path

from .app import create
from .db import check, generate, initialize

DATABASE_PATH = (Path(__file__).resolve().parent / 'db' / 'ast.db').resolve()
SCHEMA_SQL_PATH = (Path(__file__).resolve().parent / 'db' / 'schema.sql').resolve()
SCHEMA_PYDANTIC_PATH = (Path(__file__).parent / 'schema.py').resolve()

parser = argparse.ArgumentParser(prog='sqli', description='Machine Learning SQL Injection Collector')
command = parser.add_subparsers(dest='command')


def main(argv: Sequence[str] | None = None) -> int:
  db = command.add_parser('db', help='Database')
  db_command = db.add_subparsers(dest='db')

  init = db_command.add_parser('init', help='Initialize Database')
  init.add_argument('--path', type=Path, default=DATABASE_PATH, help='Path to the database schema SQL file')
  init.add_argument('--schema', type=Path, default=SCHEMA_SQL_PATH, help='Path to the database schema SQL file')

  seed = db_command.add_parser('seed', help='Seed Database')
  seed.add_argument('--url', type=str, default='http://127.0.0.1:8080', help='Flask url')
  seed.add_argument('--path', type=str, default=SCHEMA_PYDANTIC_PATH, help='Schema pydantic path')
  seed.add_argument('--name', type=str, default='UserLoginSchema', help='Schema pydantic to generate')
  seed.add_argument('--count', type=int, default=1000, help='How much data benign to generate')

  flask = command.add_parser('flask', help='Flask Server Collector')
  flask_command = flask.add_subparsers(dest='flask')

  run = flask_command.add_parser('run', help='Run Flask Server')
  run.add_argument('--label', type=int, help='Label for benign/malicious requests')
  run.add_argument(
    '--host',
    type=str,
    default='127.0.0.1',
    help='Host',
  )
  run.add_argument('--port', type=int, default=8080, help='Port')
  run.add_argument('--database', type=Path, default=DATABASE_PATH, help='Path to the database file')
  run.add_argument('--schema', type=Path, default=SCHEMA_PYDANTIC_PATH, help='Path to the pydantic schema file')

  parse = parser.parse_args(argv)

  match parse.command:
    case 'db':
      match parse.db:
        case 'init':
          initialize(parse.path, parse.schema)
        case 'seed':
          generate(parse.url, parse.name, parse.count, parse.path)
        case _:
          raise NameError('Unknown command')
    case 'flask':
      match parse.flask:
        case 'run':
          create(parse.label, parse.host, parse.port, check(parse.database), threading.Lock(), parse.schema)
        case _:
          raise NameError('Unknown command')
    case _:
      raise NameError('Unknown command')

  return 0


__all__ = ['main']
