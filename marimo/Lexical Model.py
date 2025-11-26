import marimo

__generated_with = '0.18.0'
app = marimo.App(width='medium')


@app.cell
def _():
  import marimo as mo

  return (mo,)


@app.cell
def _():
  import polars

  return (polars,)


@app.cell
def _():
  import sqlalchemy

  return (sqlalchemy,)


@app.cell
def _():
  return


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
  engine = sqlalchemy.create_engine('sqlite:///db/main.db')
  return (engine,)


@app.cell
def _(engine, lexicals, mo, payloads):
  dataset = mo.sql(
    """
        SELECT
          p.id,
          p.payload,
          p.dialect,
          p.label,
        --  p.created,
        --  a.serde,
          l.length,
          l.digit,
          l.ratio_digit,
          l.letter,
          l.ratio_letter,
          l.upper,
          l.ratio_upper,
          l.lower,
          l.ratio_lower,
          l.whitespace,
          l.ratio_whitespace,
          l.punctuation,
          l.ratio_punctuation,
          l.shannon,
          l.equal,
          l.single,
          l.double,
          l.dash,
          l.slash,
          l.star,
          l.semicolon,
          l.percent,
          l.parentheses,
          l.comma,
          l.dot,
          l.underscore,
          l.repeat,
          l.imbalance
        FROM payloads AS p
        JOIN lexicals AS l ON l.payload_id = p.id;
        """,
    engine=engine,
  )
  return (dataset,)


@app.cell
def _(dataset, polars):
  features = dataset.select(polars.all().exclude(['payload', 'dialect']))
  return (features,)


@app.cell
def _(features):
  labels = features['label']
  return (labels,)


@app.cell
def _(features, labels, train_test_split):
  feature_train, feature_test, label_train, label_test = train_test_split(
    features, labels, test_size=0.1, random_state=32, stratify=labels
  )
  return feature_test, feature_train, label_test, label_train


@app.cell
def _(StandardScaler):
  scaler = StandardScaler()
  return (scaler,)


@app.cell
def _(feature_train, scaler):
  feature_train_scaled = scaler.fit_transform(feature_train)
  return (feature_train_scaled,)


@app.cell
def _(feature_test, scaler):
  feature_test_scaled = scaler.transform(feature_test)
  return (feature_test_scaled,)


@app.cell
def _(LogisticRegression):
  lr = LogisticRegression(max_iter=64, class_weight='balanced')
  return (lr,)


@app.cell
def _(feature_train_scaled, label_train, lr):
  lr.fit(feature_train_scaled, label_train)
  return


@app.cell
def _(feature_test_scaled, lr):
  lr_predicate = lr.predict(feature_test_scaled)
  return (lr_predicate,)


@app.cell
def _(RandomForestClassifier):
  rf = RandomForestClassifier(n_estimators=128, class_weight='balanced')
  return (rf,)


@app.cell
def _(feature_train, label_train, rf):
  rf.fit(feature_train, label_train)
  return


@app.cell
def _(feature_test, rf):
  rf_predicate = rf.predict(feature_test)
  return (rf_predicate,)


@app.cell
def _(classification_report, label_test, lr_predicate):
  print(classification_report(label_test, lr_predicate))
  return


@app.cell
def _(classification_report, label_test, rf_predicate):
  print(classification_report(label_test, rf_predicate))
  return


if __name__ == '__main__':
  app.run()
