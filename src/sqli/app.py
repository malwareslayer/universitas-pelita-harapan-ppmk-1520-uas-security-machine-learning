import json
import math
import sqlite3
import threading
import warnings
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import sqlglot
from flask import Flask, jsonify, request, Response
from pydantic import BaseModel, ValidationError

flask = Flask(__name__, static_folder=None)


def depth(ast):
  if not isinstance(ast, sqlglot.exp.Expression):
    return 0

  children = []

  for child in ast.args.values():
    if isinstance(child, sqlglot.exp.Expression):
      children.append(child)
    elif isinstance(child, list):
      for v in child:
        if isinstance(v, sqlglot.exp.Expression):
          children.append(v)

  if not children:
    return 1

  return 1 + max(depth(child) for child in children)


def count(walkers: list[sqlglot.exp.Expression], node_type):
  return sum(isinstance(n, node_type) for n in walkers)


def create(host: str, port: int, db: sqlite3.Connection, lock: threading.Lock, schema: Path, **kwargs) -> None:
  cursor = db.cursor()

  defaults = {'UserLoginSchema': 'POST', 'UserInsertSchema': 'POST'}

  if not schema.exists():
    raise FileNotFoundError(f"Schema '{schema}' does not exist")

  if schema == (Path(__file__).parent / 'schema.py').resolve():
    for k, v in defaults.items():
      kwargs.setdefault(k, v)

  spec = spec_from_file_location('schema', str(schema))
  module = module_from_spec(spec)

  spec.loader.exec_module(module)

  for endpoint, method in kwargs.items():
    if not hasattr(module, endpoint):
      warnings.warn(f'Skip: schema does not have {endpoint}', stacklevel=1)
      continue

    model = getattr(module, endpoint)

    if not issubclass(model, BaseModel):
      warnings.warn(f'Skip: schema {endpoint} is not a pydantic model', stacklevel=1)
      continue

    table = getattr(model, '__table__', None)
    op = getattr(model, '__op__', 'select').lower()

    if table is None:
      raise AttributeError(f"Schema '{endpoint}' must define __table__")

    flask.config[endpoint] = {
      'model': model,
    }

    match method:
      case 'GET':
        match op:
          case 'select':
            flask.config[endpoint]['query']: str = sqlglot.select('*').from_(table).sql(dialect='sqlite')

            def view_func() -> tuple[Response, int] | Response:
              data = request.args.to_dict()

              try:
                serializer = flask.config[request.endpoint]['model'](**data)
              except ValidationError:
                return jsonify({'error': 'Invalid input'}), 400

              clauses: list[str] = []

              for name, value in serializer.model_dump().items():
                if isinstance(value, str):
                  clauses.append(f"{name} = '{value}'")

                if isinstance(value, int):
                  clauses.append(f'{name} = {value}')

              query: str = flask.config[request.endpoint]['query'] + ' ' + f'WHERE {" AND ".join(clauses)}'

              try:
                asts = sqlglot.parse(query, dialect='sqlite')
              except (sqlglot.errors.ParseError, sqlglot.errors.TokenError):
                with lock:
                  db.execute(
                    """
                    INSERT INTO payloads (payload, label, error)
                    VALUES (?, ?, ?)
                    """,
                    (query, 1, 1),
                  )

                  db.commit()

                return Response(None, status=200)
              else:
                with lock:
                  cursor.execute(
                    """
                    INSERT INTO payloads (payload, label, error)
                    VALUES (?, ?, ?)
                    """,
                    (query, 1, 0),
                  )

                  rowid = cursor.lastrowid

                  for ast in asts:
                    walkers = list(ast.walk())
                    tree = depth(ast)

                    cursor.execute(
                      """
                      INSERT INTO asts (
                        payload, ast, nodes, tree_depths, subtree_depths, literals, identifiers, binary_expressions,
                        comparisons, logical_operations, or_operations, and_operations, unions, comments, functions,
                        subqueries
                      )
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                      """,
                      (
                        rowid,
                        json.dumps(ast.dump()),
                        len(walkers),
                        tree,
                        0,
                        count(walkers, sqlglot.exp.Literal),
                        count(walkers, sqlglot.exp.Identifier),
                        count(walkers, sqlglot.exp.Binary),
                        (
                          count(walkers, sqlglot.exp.EQ)
                          + count(walkers, sqlglot.exp.NEQ)
                          + count(walkers, sqlglot.exp.GT)
                          + count(walkers, sqlglot.exp.LT)
                          + count(walkers, sqlglot.exp.GTE)
                          + count(walkers, sqlglot.exp.LTE)
                        ),
                        (count(walkers, sqlglot.exp.And) + count(walkers, sqlglot.exp.Or)),
                        count(walkers, sqlglot.exp.Or),
                        count(walkers, sqlglot.exp.And),
                        count(walkers, sqlglot.exp.Union),
                        sum(bool(n.comments) for n in walkers),
                        count(walkers, sqlglot.exp.Func),
                        count(walkers, sqlglot.exp.Subquery),
                      ),
                    )

                  length = len(query)

                  digits = sum(c.isdigit() for c in query)
                  letters = sum(c.isalpha() for c in query)
                  whitespaces = sum(c.isspace() for c in query)
                  specials = length - digits - letters - whitespaces

                  if length > 0:
                    from collections import Counter

                    counts = Counter(query)
                    entropy = 0.0
                    for counting in counts.values():
                      p = counting / length
                      entropy -= p * math.log2(p)
                  else:
                    entropy = 0.0

                  if length > 0:
                    ratio_digits = digits / length
                    ratio_special = specials / length
                    ratio_whitespace = whitespaces / length
                  else:
                    ratio_digits = 0.0
                    ratio_special = 0.0
                    ratio_whitespace = 0.0

                  cursor.execute(
                    """
                    INSERT INTO lexicals (
                      payload, length, digits, letters, whitespaces, specials, entropy, ratio_digits, ratio_special,
                      ratio_whitespace
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                      rowid,
                      length,
                      digits,
                      letters,
                      whitespaces,
                      specials,
                      entropy,
                      ratio_digits,
                      ratio_special,
                      ratio_whitespace,
                    ),
                  )

                  db.commit()

              return Response(None, status=200)

            flask.add_url_rule(
              f'/{endpoint}',
              endpoint=endpoint,
              view_func=view_func,
              methods=[method],
            )

          case _:
            raise RuntimeError(f"Unsupported operation '{op}' for method GET in schema '{endpoint}'")
      case 'POST':
        match op:
          case 'select':
            flask.config[endpoint]['query'] = sqlglot.select('*').from_(table).sql(dialect='sqlite')

            def view_func() -> tuple[Response, int] | Response:
              data = request.get_json()

              try:
                serializer = flask.config[request.endpoint]['model'](**data)
              except ValidationError:
                return jsonify({'error': 'Invalid input'}), 400

              clauses = []

              for name, value in serializer.model_dump().items():
                if isinstance(value, str):
                  clauses.append(f"{name} = '{value}'")

                if isinstance(value, int):
                  clauses.append(f'{name} = {value}')

              query = flask.config[request.endpoint]['query'] + ' ' + f'WHERE {" AND ".join(clauses)}'

              try:
                asts = sqlglot.parse(query, dialect='sqlite')
              except (sqlglot.errors.ParseError, sqlglot.errors.TokenError):
                with lock:
                  db.execute(
                    """
                    INSERT INTO payloads (payload, label, error)
                    VALUES (?, ?, ?)
                    """,
                    (query, 1, 1),
                  )

                  db.commit()

                return Response(None, status=200)
              else:
                with lock:
                  cursor.execute(
                    """
                    INSERT INTO payloads (payload, label, error)
                    VALUES (?, ?, ?)
                    """,
                    (query, 1, 0),
                  )

                  rowid = cursor.lastrowid

                  for ast in asts:
                    walkers = list(ast.walk())
                    tree = depth(ast)

                    cursor.execute(
                      """
                      INSERT INTO asts (
                        payload, ast, nodes, tree_depths, subtree_depths, literals, identifiers, binary_expressions,
                        comparisons, logical_operations, or_operations, and_operations, unions, comments, functions,
                        subqueries
                      )
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                      """,
                      (
                        rowid,
                        json.dumps(ast.dump()),
                        len(walkers),
                        tree,
                        0,
                        count(walkers, sqlglot.exp.Literal),
                        count(walkers, sqlglot.exp.Identifier),
                        count(walkers, sqlglot.exp.Binary),
                        (
                          count(walkers, sqlglot.exp.EQ)
                          + count(walkers, sqlglot.exp.NEQ)
                          + count(walkers, sqlglot.exp.GT)
                          + count(walkers, sqlglot.exp.LT)
                          + count(walkers, sqlglot.exp.GTE)
                          + count(walkers, sqlglot.exp.LTE)
                        ),
                        (count(walkers, sqlglot.exp.And) + count(walkers, sqlglot.exp.Or)),
                        count(walkers, sqlglot.exp.Or),
                        count(walkers, sqlglot.exp.And),
                        count(walkers, sqlglot.exp.Union),
                        sum(bool(n.comments) for n in walkers),
                        count(walkers, sqlglot.exp.Func),
                        count(walkers, sqlglot.exp.Subquery),
                      ),
                    )

                  length = len(query)

                  digits = sum(c.isdigit() for c in query)
                  letters = sum(c.isalpha() for c in query)
                  whitespaces = sum(c.isspace() for c in query)
                  specials = length - digits - letters - whitespaces

                  if length > 0:
                    from collections import Counter

                    counts = Counter(query)
                    entropy = 0.0
                    for counting in counts.values():
                      p = counting / length
                      entropy -= p * math.log2(p)
                  else:
                    entropy = 0.0

                  if length > 0:
                    ratio_digits = digits / length
                    ratio_special = specials / length
                    ratio_whitespace = whitespaces / length
                  else:
                    ratio_digits = 0.0
                    ratio_special = 0.0
                    ratio_whitespace = 0.0

                  cursor.execute(
                    """
                    INSERT INTO lexicals (
                      payload, length, digits, letters, whitespaces, specials, entropy, ratio_digits, ratio_special,
                      ratio_whitespace
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                      rowid,
                      length,
                      digits,
                      letters,
                      whitespaces,
                      specials,
                      entropy,
                      ratio_digits,
                      ratio_special,
                      ratio_whitespace,
                    ),
                  )

                  db.commit()

              return Response(None, status=200)

            flask.add_url_rule(
              f'/{endpoint}',
              endpoint=endpoint,
              view_func=view_func,
              methods=[method],
            )
          case 'insert':
            flask.config[endpoint]['query'] = sqlglot.insert('V', table).sql(dialect='sqlite')

            def view_func() -> tuple[Response, int] | Response:
              data = request.get_json()

              try:
                serializer = flask.config[request.endpoint]['model'](**data)
              except ValidationError:
                return jsonify({'error': 'Invalid input'}), 400

              columns = []
              values = []

              for name, value in serializer.model_dump().items():
                columns.append(name)

                if isinstance(value, str):
                  values.append(f"'{value}'")

                if isinstance(value, int):
                  values.append(f'{value}')

              query = flask.config[request.endpoint]['query'].replace(
                'V', f'({", ".join(columns)}) VALUES ({", ".join(values)})'
              )

              try:
                asts = sqlglot.parse(query, dialect='sqlite')
              except (sqlglot.errors.ParseError, sqlglot.errors.TokenError):
                with lock:
                  db.execute(
                    """
                    INSERT INTO payloads (payload, label, error)
                    VALUES (?, ?, ?)
                    """,
                    (query, 1, 1),
                  )

                  db.commit()

                return Response(None, status=200)
              else:
                with lock:
                  cursor.execute(
                    """
                    INSERT INTO payloads (payload, label, error)
                    VALUES (?, ?, ?)
                    """,
                    (query, 1, 0),
                  )

                  rowid = cursor.lastrowid

                  for ast in asts:
                    walkers = list(ast.walk())
                    tree = depth(ast)

                    cursor.execute(
                      """
                      INSERT INTO asts (
                        payload, ast, nodes, tree_depths, subtree_depths, literals, identifiers, binary_expressions,
                        comparisons, logical_operations, or_operations, and_operations, unions, comments, functions,
                        subqueries
                      )
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                      """,
                      (
                        rowid,
                        json.dumps(ast.dump()),
                        len(walkers),
                        tree,
                        0,
                        count(walkers, sqlglot.exp.Literal),
                        count(walkers, sqlglot.exp.Identifier),
                        count(walkers, sqlglot.exp.Binary),
                        (
                          count(walkers, sqlglot.exp.EQ)
                          + count(walkers, sqlglot.exp.NEQ)
                          + count(walkers, sqlglot.exp.GT)
                          + count(walkers, sqlglot.exp.LT)
                          + count(walkers, sqlglot.exp.GTE)
                          + count(walkers, sqlglot.exp.LTE)
                        ),
                        (count(walkers, sqlglot.exp.And) + count(walkers, sqlglot.exp.Or)),
                        count(walkers, sqlglot.exp.Or),
                        count(walkers, sqlglot.exp.And),
                        count(walkers, sqlglot.exp.Union),
                        sum(bool(n.comments) for n in walkers),
                        count(walkers, sqlglot.exp.Func),
                        count(walkers, sqlglot.exp.Subquery),
                      ),
                    )

                  length = len(query)

                  digits = sum(c.isdigit() for c in query)
                  letters = sum(c.isalpha() for c in query)
                  whitespaces = sum(c.isspace() for c in query)
                  specials = length - digits - letters - whitespaces

                  if length > 0:
                    from collections import Counter

                    counts = Counter(query)
                    entropy = 0.0
                    for counting in counts.values():
                      p = counting / length
                      entropy -= p * math.log2(p)
                  else:
                    entropy = 0.0

                  if length > 0:
                    ratio_digits = digits / length
                    ratio_special = specials / length
                    ratio_whitespace = whitespaces / length
                  else:
                    ratio_digits = 0.0
                    ratio_special = 0.0
                    ratio_whitespace = 0.0

                  cursor.execute(
                    """
                    INSERT INTO lexicals (
                      payload, length, digits, letters, whitespaces, specials, entropy, ratio_digits, ratio_special,
                      ratio_whitespace
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                      rowid,
                      length,
                      digits,
                      letters,
                      whitespaces,
                      specials,
                      entropy,
                      ratio_digits,
                      ratio_special,
                      ratio_whitespace,
                    ),
                  )

                  db.commit()

              return Response(None, status=200)

            flask.add_url_rule(
              f'/{endpoint}',
              endpoint=endpoint,
              view_func=view_func,
              methods=[method],
            )
          case _:
            raise RuntimeError(f"Unsupported operation '{op}' for method POST in schema '{endpoint}'")
      case _:
        raise RuntimeError(f"Unsupported method '{method}' for schema '{endpoint}'")

  routes = [rule.endpoint for rule in flask.url_map.iter_rules()]

  if not routes:
    raise RuntimeError('Flask has no active schema routes registered')

  flask.run(host=host, port=port, debug=True)


__all__ = ['create']
