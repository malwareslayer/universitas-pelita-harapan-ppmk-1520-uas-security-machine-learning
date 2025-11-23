import argparse
import sys
from collections.abc import Sequence
from importlib import import_module
from pathlib import Path

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.exc import ArgumentError, OperationalError

from .schema import __base__

argument = argparse.ArgumentParser(prog='ml', description='Machine Learning SQL Injection Collector')
command = argument.add_subparsers(dest='command')


def main(argv: Sequence[str] | None = None) -> int:
  database = command.add_parser('db', help='Database')
  db = database.add_subparsers(dest='db')

  create = db.add_parser('create', help='Initialize Database')

  create.add_argument(
    'url',
    type=str,
    nargs='?',
    default=f'sqlite://{str(Path(__file__).absolute().parent.parent.parent)}/db/main.db',
    help='Path To Create The Database For Storing Ingestion Payload Malicious & Benign',
  )

  scenario = command.add_parser('scenario', help='Database')

  scenario.add_argument(
    'modules',
    type=Path,
    nargs='?',
    default=Path(__file__).resolve().parents[1] / 'scenario' / 'sqli',
    help='Path To The Flask Application Module',
  )

  scenario.add_argument('--name', type=str, default='app', help='The Flask Application Object Name')

  parse = argument.parse_args(argv)

  match parse.command:
    case 'db':
      match parse.db:
        case 'create':
          engine = create_engine(parse.url)

          try:
            __base__.metadata.create_all(engine)
          except (ArgumentError, OperationalError, Exception) as e:
            raise ConnectionError(str(e)) from e
        case _:
          raise AttributeError('Unknown Command')
    case 'scenario':
      package: Path = parse.modules

      if not package.is_dir() or not package.exists():
        raise NameError(f'Path {str(package)} Is Not A Directory Or Does Not Exists')

      if not (package / '__init__.py').exists():
        raise ImportError(f'Path {str(package)} Is Not A Valid Python Package')

      base = str(package.parent.resolve())

      if base not in sys.path:
        sys.path.insert(0, base)

      try:
        module = import_module(package.name)
      except ImportError:
        raise ImportError(f'Cannot import module from {package}') from ImportError

      if not hasattr(module, parse.name):
        raise AttributeError(f'Module {str(package)} does not have an attribute named "{parse.name}"')

      app = getattr(module, parse.name)

      if not isinstance(app, Flask):
        raise TypeError(f'Attribute "{parse.name}" in module {package} is not a Flask instance')

      app.run(host='127.0.0.1', port=8080, debug=True)
    case _:
      raise AttributeError('Unknown Command')

  return 0


__all__ = ['main']
