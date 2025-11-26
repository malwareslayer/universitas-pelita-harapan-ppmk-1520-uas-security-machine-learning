import argparse
import sys
from collections.abc import Sequence
from importlib import import_module
from pathlib import Path

import requests
from flask import Flask
from parser import Base
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
    default='sqlite:///db/main.db',
    help='Path To Create The Database For Storing Ingestion Payload Malicious & Benign',
  )

  fake = db.add_parser('fake', help='Fake Database')
  fake.add_argument(
    'modules',
    type=Path,
    nargs='?',
    default=Path(__file__).resolve().parents[1] / 'scenario' / 'sqli',
    help='Path To The Flask Application Module',
  )
  fake.add_argument('--name', type=str, default='User', help='Model In Schema Module')
  fake.add_argument('--count', type=int, default=2048, help='Host')
  fake.add_argument('--method', type=str, default='GET', help='Host')
  fake.add_argument('--url', type=str, default='http://127.0.0.1:8080', help='Host')

  scenario = command.add_parser('scenario', help='Database')
  scenario.add_argument(
    'modules',
    type=Path,
    nargs='?',
    default=Path(__file__).resolve().parents[1] / 'scenario' / 'sqli',
    help='Path To The Flask Application Module',
  )
  scenario.add_argument('--name', type=str, default='app', help='The Flask Application Object Name')
  scenario.add_argument('--host', type=str, default='127.0.0.1', help='Host')
  scenario.add_argument('--port', type=int, default=8080, help='Port')

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
        case 'fake':
          if parse.method not in ['GET', 'POST', 'PUT']:
            raise ValueError('Method Not Allowed')

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

          if not hasattr(module, 'schema'):
            raise AttributeError(f'Module {str(package)} does not have an module named "schema"')

          schema = module.schema

          if not hasattr(schema, parse.name):
            raise AttributeError(f'Module {str(package)} does not have an class names "{parse.name}"')

          model = getattr(schema, parse.name)

          if not issubclass(model, Base):
            raise ReferenceError(f'class "{parse.name}" is not a subclass of Base"')

          for _ in range(parse.count):
            data = model.fake().to_dict()

            match parse.method:
              case 'GET':
                data.pop('id')

                requests.request(
                  parse.method,
                  f'{parse.url}/{model.__tablename__}',
                  params=data,
                  headers={'X-Payload-Label': '0'},
                )
              case 'POST':
                requests.request(
                  parse.method,
                  f'{parse.url}/{model.__tablename__}',
                  json=data,
                  headers={'X-Payload-Label': '0'},
                )
              case 'UPDATE':
                requests.request(
                  parse.method,
                  f'{parse.url}/{model.__tablename__}',
                  params={'id': 1},
                  json=data,
                  headers={'X-Payload-Label': '0'},
                )
              case _:
                raise ValueError('Method Not Allowed')
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
