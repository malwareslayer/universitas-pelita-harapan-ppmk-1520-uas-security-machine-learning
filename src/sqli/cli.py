import argparse
import threading
from collections.abc import Sequence
from pathlib import Path

from .app import create
from .db import check, initialize

DATABASE_PATH = (Path(__file__).resolve().parent / 'db' / 'ast.db').resolve()

parser = argparse.ArgumentParser(prog='sqli', description='Machine Learning SQL Injection Collector')

sub = parser.add_subparsers(dest='command')


def main(argv: Sequence[str] = None) -> int:
  db = sub.add_parser('db', help='Database')
  db_command = db.add_subparsers(dest='db')

  init = db_command.add_parser('init', help='Initialize Database')
  init.add_argument('--path', type=Path, default=DATABASE_PATH, help='Path to the database schema SQL file')

  flask = sub.add_parser('flask', help='Flask Server Collector')
  flask_command = flask.add_subparsers(dest='flask')

  run = flask_command.add_parser('run', help='Run Flask Server')
  run.add_argument(
    '--host',
    type=str,
    default='127.0.0.1',
    help='Host',
  )
  run.add_argument('--port', type=int, default=8080, help='Port')
  run.add_argument('--database', type=Path, default=DATABASE_PATH, help='Path to the database file')
  run.add_argument('--schema', type=Path, help='Path to the pydantic schema file')

  args = parser.parse_args(argv)

  match args.command:
    case 'db':
      match args.db:
        case 'init':
          initialize(args.path)
        case _:
          raise NameError('Unknown command')
    case 'flask':
      match args.flask:
        case 'run':
          create(args.host, args.port, check(args.database), threading.Lock(), args.schema)
        case _:
          raise NameError('Unknown command')
    case _:
      raise NameError('Unknown command')

  return 0


__all__ = ['main']
