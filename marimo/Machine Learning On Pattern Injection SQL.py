import marimo

__generated_with = '0.17.8'
app = marimo.App(width='medium')


@app.cell
def _():
  import marimo as mo

  return (mo,)


@app.cell
def _():
  import sqlalchemy

  return (sqlalchemy,)


@app.cell
def _():
  from sklearn.model_selection import train_test_split

  return (train_test_split,)


@app.cell
def _():
  from sklearn.preprocessing import StandardScaler

  return (StandardScaler,)


@app.cell
def _():
  from sklearn.linear_model import LogisticRegression

  return (LogisticRegression,)


@app.cell
def _():
  from sklearn.ensemble import RandomForestClassifier

  return (RandomForestClassifier,)


@app.cell
def _():
  from sklearn.metrics import classification_report

  return (classification_report,)


@app.cell
def _(sqlalchemy):
  sqlite_engine = sqlalchemy.create_engine('sqlite:///src/sqli/db/ast.db')
  return (sqlite_engine,)


@app.cell
def _(asts, lexicals, mo, payloads, sqlite_engine):
  dataset = mo.sql(
    """
        SELECT
          p.id,
          p.payload,
          p.label,
          p.error,
          a.nodes,
          a.tree_depths,
          a.subtree_depths,
          a.literals,
          a.identifiers,
          a.binary_expressions,
          a.comparisons,
          a.logical_operations,
          a.or_operations,
          a.and_operations,
          a.unions,
          a.comments,
          a.functions,
          a.subqueries,
          l.length,
          l.digits,
          l.letters,
          l.whitespaces,
          l.specials,
          l.entropy,
          l.ratio_digits,
          l.ratio_special,
          l.ratio_whitespace
        FROM payloads   AS p
        JOIN asts       AS a ON a.payload = p.id
        JOIN lexicals   AS l ON l.payload = p.id;
        """,
    engine=sqlite_engine,
  )
  return (dataset,)


@app.cell
def _():
  features = [
    'nodes',
    'tree_depths',
    'subtree_depths',
    'literals',
    'identifiers',
    'binary_expressions',
    'comparisons',
    'logical_operations',
    'or_operations',
    'and_operations',
    'unions',
    'comments',
    'functions',
    'subqueries',
    'length',
    'digits',
    'letters',
    'whitespaces',
    'specials',
    'entropy',
    'ratio_digits',
    'ratio_special',
    'ratio_whitespace',
  ]
  return (features,)


@app.cell
def _(dataset, features):
  x = dataset[features]
  return (x,)


@app.cell
def _(dataset):
  y = dataset['label']
  return (y,)


@app.cell
def _(train_test_split, x, y):
  X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.1, random_state=50, stratify=y)
  return X_test, X_train, Y_test, Y_train


@app.cell
def _(StandardScaler):
  scaler = StandardScaler()
  return (scaler,)


@app.cell
def _(X_train, scaler):
  X_train_scaled = scaler.fit_transform(X_train)
  return (X_train_scaled,)


@app.cell
def _(X_test, scaler):
  X_test_scaled = scaler.transform(X_test)
  return (X_test_scaled,)


@app.cell
def _(LogisticRegression):
  lr = LogisticRegression(max_iter=100, class_weight='balanced')
  return (lr,)


@app.cell
def _(X_train_scaled, Y_train, lr):
  lr.fit(X_train_scaled, Y_train)
  return


@app.cell
def _(X_test_scaled, lr):
  lr_predicate = lr.predict(X_test_scaled)
  return (lr_predicate,)


@app.cell
def _(RandomForestClassifier):
  rf = RandomForestClassifier(n_estimators=300, max_depth=None, class_weight='balanced')
  return (rf,)


@app.cell
def _(X_train, Y_train, rf):
  rf.fit(X_train, Y_train)
  return


@app.cell
def _(X_test, rf):
  rf_predicate = rf.predict(X_test)
  return (rf_predicate,)


@app.cell
def _(Y_test, classification_report, lr_predicate):
  print(classification_report(Y_test, lr_predicate))
  return


@app.cell
def _(Y_test, classification_report, rf_predicate):
  print(classification_report(Y_test, rf_predicate))
  return


if __name__ == '__main__':
  app.run()
