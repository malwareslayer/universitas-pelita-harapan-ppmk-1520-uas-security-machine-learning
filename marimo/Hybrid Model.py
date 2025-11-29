import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import numpy
    return (numpy,)


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
    import altair
    return (altair,)


@app.cell
def _():
    from typing import Dict, List, Tuple
    return Dict, List


@app.cell
def _():
    from matplotlib import pyplot
    return (pyplot,)


@app.cell
def _():
    from sklearn.model_selection import train_test_split
    return (train_test_split,)


@app.cell
def _():
    from sklearn.ensemble import ExtraTreesClassifier
    return (ExtraTreesClassifier,)


@app.cell
def _():
    from sklearn.linear_model import LogisticRegression, SGDClassifier
    return LogisticRegression, SGDClassifier


@app.cell
def _():
    from sklearn.preprocessing import StandardScaler
    return (StandardScaler,)


@app.cell
def _():
    from sklearn.model_selection import StratifiedKFold
    return (StratifiedKFold,)


@app.cell
def _():
    from sklearn.feature_selection import RFE
    return


@app.cell
def _():
    from sklearn.metrics import (
      classification_report,
      confusion_matrix,
      roc_curve,
      roc_auc_score,
      log_loss,
      accuracy_score,
      ConfusionMatrixDisplay
    )
    return (
        ConfusionMatrixDisplay,
        accuracy_score,
        classification_report,
        log_loss,
    )


@app.cell
def _():
    from xgboost import XGBClassifier
    return (XGBClassifier,)


@app.cell
def _(sqlalchemy):
    engine = sqlalchemy.create_engine('sqlite:///db/main.db')
    return (engine,)


@app.cell
def _(asts, engine, lexicals, mo, payloads):
    dataset = mo.sql(
        f"""
        SELECT
          p.payload,
          p.dialect,
          p.label,
          a.node,
          a.leaf,
        --  a.subquery,
        --  a.'select',
        --  a.'from',
        --  a.'insert',
        --  a.'update',
        --  a.'delete',
        --  a.'create',
        --  a.'drop',
        --  a.'alter',
        --  a.'where',
        --  a.'having',
        --  a.'union',
        --  a.'intersect',
        --  a.'except',
        --  a.'join',
        --  a.'limit',
        --  a.'offset',
        --  a.'order',
        --  a.'group',
        --  a.'cte',
        --  a.'with',
        --  a.literal,
        --  a.string,
        --  a.number,
          a.identifier,
        --  a.star,
        --  a.'null',
        --  a.dpipe,
        --  a.binary,
        --  a.'add',
        --  a.'sub',
        --  a.'mul',
        --  a.'div',
        --  a.'mod',
        --  a.eq,
        --  a.neq,
        --  a.gt,
        --  a.gte,
        --  a.lt,
        --  a.lte,
        --  a.'between',
        --  a.'case',
        --  a.'like',
          a.predicate,
          a.condition,
        --  a.'or',
        --  a.'and',
        --  a.'not',
        --  a.bitwiseor,
        --  a.bitwiseand,
        --  a.bitwisexor,
          a.func,
        --  a.comment
        --  l.length,
        --  l.digit,
          l.letter,
        --  l.upper,
        --  l.lower,
        --  l.comment,
          l.whitespace
        --  l.punctuation
        --  l.single,
        --  l.equal,
        --  l.dash
        --  l.pipe
        --  l.parentheses
        --  l.comma
        FROM payloads AS p
        JOIN asts     AS a ON a.payload_id = p.id
        JOIN lexicals AS l ON l.payload_id = p.id;
        """,
        output=False,
        engine=engine
    )
    return (dataset,)


@app.cell
def _(dataset, polars):
    selection = dataset.select(polars.all().exclude(['id', 'payload', 'dialect']))
    return (selection,)


@app.cell
def _(polars, selection):
    features = selection.select(polars.all().exclude(['label']))
    return (features,)


@app.cell
def _(features):
    features
    return


@app.cell
def _(selection):
    labels = selection['label']
    return (labels,)


@app.cell
def _(features, labels, train_test_split):
    feature_train, feature_test, label_train, label_test = train_test_split(
      features, labels, test_size=0.35, random_state=32, stratify=labels
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
def _(ExtraTreesClassifier):
    tree = ExtraTreesClassifier(n_estimators=8192, class_weight='balanced')
    return (tree,)


@app.cell
def _(feature_train_scaled, label_train, tree):
    tree.fit(feature_train_scaled, label_train)
    return


@app.cell(hide_code=True)
def _(features, tree):
    _importances = tree.feature_importances_
    _pairs = sorted(zip(features.columns, _importances), key=lambda x: x[1], reverse=True)

    for _name, _score in _pairs:
        print(f"{_name}: {_score:.4f}")
    return


@app.cell
def _(LogisticRegression):
    lr = LogisticRegression(max_iter=8192, class_weight='balanced', solver='saga', random_state=32, C=0.1)
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
def _(XGBClassifier):
    rf = XGBClassifier(n_estimators=8192, max_depth=4, learning_rate=0.1, subsample=0.8, gamma=1, reg_lambda=1, reg_alpha=0, eval_metric='logloss', tree_method='hist', random_state=32)
    return (rf,)


@app.cell
def _(feature_train_scaled, label_train, rf):
    rf.fit(feature_train_scaled, label_train)
    return


@app.cell
def _(feature_test_scaled, rf):
    rf_predicate = rf.predict(feature_test_scaled)
    return (rf_predicate,)


@app.cell(hide_code=True)
def _(classification_report, label_test, lr_predicate):
    print(classification_report(label_test, lr_predicate, digits=4))
    return


@app.cell(hide_code=True)
def _(classification_report, label_test, rf_predicate):
    print(classification_report(label_test, rf_predicate, digits=4))
    return


@app.cell(hide_code=True)
def _(ConfusionMatrixDisplay, label_test, lr_predicate, pyplot, rf_predicate):
    _figure, _axes = pyplot.subplots(1, 2, figsize=(12, 5))

    ConfusionMatrixDisplay.from_predictions(
        label_test,
        lr_predicate,
        ax=_axes[0],
        cmap="Blues",
        colorbar=False
    )
    _axes[0].set_title("Logistic Regression - Confusion Matrix")
    _axes[0].set_xlabel("Predicted label")
    _axes[0].set_ylabel("True label")

    ConfusionMatrixDisplay.from_predictions(
        label_test,
        rf_predicate,
        ax=_axes[1],
        cmap="Greens",
        colorbar=False
    )
    _axes[1].set_title("Random Forest - Confusion Matrix")
    _axes[1].set_xlabel("Predicted label")
    _axes[1].set_ylabel("True label")

    pyplot.tight_layout()
    pyplot.gca()
    return


@app.cell(hide_code=True)
def _(
    List,
    SGDClassifier,
    accuracy_score,
    feature_test_scaled,
    feature_train_scaled,
    label_test,
    label_train,
    log_loss,
    numpy,
    pyplot,
):
    sgd: SGDClassifier = SGDClassifier(loss="log_loss", max_iter=2048, learning_rate="optimal", warm_start=True, random_state=32)

    _classes: numpy.ndarray = numpy.unique(numpy.array(label_train))

    _epochs: int = 30

    _train_losses: List[float] = []
    _losses: List[float] = []

    _train_accuracies: List[float] = []
    _accuracies: List[float] = []

    for _epoch in range(_epochs):
        sgd.partial_fit(feature_train_scaled, label_train, classes=_classes)

        _train_probability: numpy.ndarray = sgd.predict_proba(feature_train_scaled)
        _probability: numpy.ndarray = sgd.predict_proba(feature_test_scaled)

        _train_loss: float = log_loss(label_train, _train_probability, labels=_classes)
        _loss: float = log_loss(label_test, _probability, labels=_classes)

        _train_predicate: numpy.ndarray = sgd.predict(feature_train_scaled)
        _predicate: numpy.ndarray = sgd.predict(feature_test_scaled)

        _train_accuracy: float = accuracy_score(label_train, _train_predicate)
        _accuracy: float = accuracy_score(label_test, _predicate)

        _train_losses.append(_train_loss)
        _losses.append(_loss)
        _train_accuracies.append(_train_accuracy)
        _accuracies.append(_accuracy)

    _figure, _axes = pyplot.subplots(1, 2, figsize=(14, 5))

    _range: numpy.ndarray = numpy.arange(1, _epochs + 1)
    _axes[0].plot(_range, _train_losses, label="Training Loss", color="royalblue", linewidth=2, marker="o")
    _axes[0].plot(_range, _losses, label="Validation Loss", color="tomato", linewidth=2, marker="o")
    _axes[0].set_title("Training and Validation Loss by Epoch")
    _axes[0].set_xlabel("Epoch")
    _axes[0].set_ylabel("Log Loss")
    _axes[0].legend(loc="best")
    _axes[0].grid(alpha=0.3)

    _axes[1].plot(_range, _train_accuracies, label="Training Accuracy", color="forestgreen", linewidth=2, marker="o")
    _axes[1].plot(_range, _accuracies, label="Validation Accuracy", color="darkorange", linewidth=2, marker="o")
    _axes[1].set_title("Training and Validation Accuracy by Epoch")
    _axes[1].set_xlabel("Epoch")
    _axes[1].set_ylabel("Accuracy")
    _axes[1].legend(loc="best")
    _axes[1].grid(alpha=0.3)

    pyplot.tight_layout()
    pyplot.gca()
    return


@app.cell(hide_code=True)
def _(
    Dict,
    List,
    LogisticRegression,
    StandardScaler,
    StratifiedKFold,
    accuracy_score,
    altair,
    features,
    labels,
    polars,
):
    _records: List[Dict[str, object]] = []

    for split in [5, 10]:
      _skf: StratifiedKFold = StratifiedKFold(n_splits=split, shuffle=True, random_state=32)

      for _fold, (_train, _valid) in enumerate(_skf.split(features, labels), start=1):
        _feature_train = features[_train]
        _feature_valid = features[_valid]
        _label_train = labels[_train]
        _label_valid = labels[_valid]

        _scaler = StandardScaler()
        _feature_train_scaled = _scaler.fit_transform(_feature_train)
        _feature_valid_scaled = _scaler.transform(_feature_valid)

        _lr = LogisticRegression(max_iter=8192, class_weight='balanced', solver='saga', random_state=32, C=0.8)
        _lr.fit(_feature_train_scaled, _label_train)

        _lr_predicate = _lr.predict(_feature_valid_scaled)
        _acc = accuracy_score(_label_valid, _lr_predicate)

        _records.append({
          "n_splits": [5, 10],
          "model": "Logistic Regression",
          "fold": _fold,
          "accuracy": _acc
        })

    _r = polars.DataFrame(_records)

    _chart = altair.Chart(_r).mark_line(point=True).encode(
        x=altair.X("fold:Q", title="Fold"),
        y=altair.Y("accuracy:Q", title="Accuracy", scale=altair.Scale(domain=[0, 1])),
        color=altair.Color("model:N", title="Model"),
        strokeDash=altair.StrokeDash("n_splits:N", title="StratifiedKFold (splits)"),
        tooltip=[
            altair.Tooltip("model:N", title="Model"),
            altair.Tooltip("n_splits:N", title="# Splits"),
            altair.Tooltip("fold:Q", title="Fold"),
            altair.Tooltip("accuracy:Q", title="Accuracy", format=".4f")
        ]
    ).properties(
        title="StratifiedKFold Cross-Validation (5 and 10 Splits)"
    ).interactive()

    _chart
    return


if __name__ == "__main__":
    app.run()
