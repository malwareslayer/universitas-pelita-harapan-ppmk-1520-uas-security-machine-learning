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
    from typing import Tuple, List
    return (List,)


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
          a.leaf,
          a.literal,
          a.identifier,
          a.binary,
          a.predicate,
          a.condition,
          a.func
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
    features = selection.select(polars.all().exclude(['label', 'payload_id', 'serde']))
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
    tree = ExtraTreesClassifier(n_estimators=4096, max_depth=4, class_weight='balanced')
    return (tree,)


@app.cell
def _(feature_train_scaled, label_train, tree):
    tree.fit(feature_train_scaled, label_train)
    return


@app.cell
def _(tree):
    importances = tree.feature_importances_
    return (importances,)


@app.cell
def _(features, importances):
    pairs = sorted(zip(features.columns, importances), key=lambda x: x[1], reverse=True)
    return (pairs,)


@app.cell(hide_code=True)
def _(pairs):
    for name, score in pairs:
        print(f"{name}: {score:.4f}")
    return


@app.cell
def _(LogisticRegression):
    lr = LogisticRegression(max_iter=8192, class_weight='balanced', solver='saga', random_state=32, C=0.8)
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
    rf = XGBClassifier(n_estimators=4096, max_depth=4, learning_rate=0.1, subsample=0.8, gamma=1, reg_lambda=1, reg_alpha=0, eval_metric='logloss', tree_method='hist', random_state=32)
    return (rf,)


@app.cell
def _(feature_train_scaled, label_train, rf):
    rf.fit(feature_train_scaled, label_train)
    return


@app.cell
def _(feature_test_scaled, rf):
    rf_predicate = rf.predict(feature_test_scaled)
    return (rf_predicate,)


@app.cell
def _(classification_report, label_test, lr_predicate):
    print(classification_report(label_test, lr_predicate, digits=4))
    return


@app.cell
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


if __name__ == "__main__":
    app.run()
