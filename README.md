# Universitas Pelita Harapan UAS Project PPMK 1520

Machine Learning SQL & XSS Injection Detection

---

## Overview

This project is a **research toolkit** for collecting and analyzing SQL injection (and related) payloads using
machine learning. It provides:

- A command‑line interface to manage the feature database and generate synthetic traffic.
- A vulnerable SQL injection web scenario for safely collecting payloads in a controlled environment.
- A schema that stores raw payloads together with derived structural and lexical features for ML experiments.

> The internal feature extraction and model logic are intentionally **not** documented here. This README focuses
> on how to use the toolkit, not how the underlying ML or AST metrics work.

---

## Installation

### Requirements

- Python **3.11 – < 4.0**
- Recommended: virtual environment (e.g. `venv`, `poetry env`, or similar)

### Install from source (using Poetry)

From the project root:

```bash
poetry install
```

This will install the package and its dependencies, and register the `ml` console script.

If you prefer plain `pip`, you can build a wheel/sdist with Poetry and install that wheel into your environment.

---

## Command‑Line Interface (CLI)

After installation, the main entry point is:

```bash
ml
```

The CLI currently focuses on **SQL injection** data collection:

- `ml db create` – initialize the feature database.
- `ml db fake` – send synthetic benign traffic to a running scenario.
- `ml scenario` – run a vulnerable HTTP scenario application.

### 1. Initialize the database

```bash
ml db create
```

Arguments:

- `url` (optional positional): SQLAlchemy‑style database URL.
  - Default: `sqlite:///db/main.db`

This creates all required tables used to store:

- Raw payload strings and labels.
- High‑level structural/AST‑style features.
- Lexical (string‑based) features.

You can point `url` to any SQLAlchemy‑compatible backend (e.g. SQLite, PostgreSQL) if you want to host the data
elsewhere.

### 2. Run the vulnerable SQLi scenario

```bash
ml scenario
```

Arguments:

- `modules` (optional positional):
  - Path to a Python package directory containing a scenario (must have `__init__.py`).
  - Default: the built‑in SQLi scenario under `src/scenario/sqli`.
- `--name` (default: `app`):
  - Name of the Flask application object in the scenario package.
- `--host` (default: `127.0.0.1`)
- `--port` (default: `8080`)

This imports the scenario package, obtains the Flask `app`, checks that it is a valid Flask instance, then runs it
with debug mode enabled on the given host and port.

**Important:** The provided scenario is intentionally **vulnerable** and must only be run in an isolated, local,
non‑production environment.

### 3. Generate fake benign traffic

With the scenario running (e.g. on `http://127.0.0.1:8080`), you can generate a batch of benign requests for the
feature database:

```bash
ml db fake --count 2048
```

Arguments:

- `modules` (optional positional):
  - Path to a scenario package directory (must have `__init__.py`).
  - Default: `src/scenario/sqli`.
- `--name` (default: `User`):
  - Name of the model class inside the scenario's `schema` module used for data generation.
- `--count` (default: `2048`):
  - Number of synthetic records to generate and send.
- `--method` (default: `GET`):
  - HTTP method used when sending requests (`GET`, `POST` or `PUT`).
- `--url` (default: `http://127.0.0.1:8080`):
  - Base URL of the running scenario application.

Behaviour (high level):

1. The CLI loads the specified scenario package and its `schema` module.
2. It retrieves the requested model class (e.g. `User`) and verifies it subclasses the common `Base`.
3. For each record:
   - A fake instance is generated and converted to a dictionary.
   - A request is sent to `BASE_URL/{table_name}` with the generated data.
   - Header `X-Payload-Label: 0` is added to mark these payloads as benign in the database.

These interactions populate the database with **labeled benign payloads** and derived features, ready for ML
experiments.

---

## Built‑In SQL Injection Scenario

The repository includes a reference SQL injection scenario under `src/scenario/sqli`.

### Scenario components

- `scenario.sqli.app`
  - A Flask application that exposes HTTP endpoints for a simple `user` resource.
  - Backed by a SQL database (SQLite by default via `db/main.db`).
  - Designed to be vulnerable for research and testing purposes.

- `scenario.sqli.schema`
  - Defines a `User` model class representing a `user` table.
  - Uses a shared `Base` and a `FakeColumn` helper to describe columns and how to generate realistic fake data
    (via the `faker` library) for fields such as:
    - `id`
    - `name`
    - `username`
    - `email`

Together, these components let you:

1. Start the vulnerable app locally (`ml scenario`).
2. Hit the endpoints manually (with crafted SQLi payloads) or automatically (via `ml db fake`).
3. Store the resulting payloads and their features in the configured database.

### Creating your own scenario (high‑level)

You can define your own scenario package following the same pattern:

1. Create a new directory (Python package) with an `__init__.py`.
2. Add a `schema.py` module that:
   - Imports `Base` and `FakeColumn` from the `parser` package.
   - Defines classes representing your tables, using SQLAlchemy column types and `FakeColumn` for fake data.
3. Expose a Flask `app` object that:
   - Connects to your desired database.
   - Registers endpoints for your schema models.

Then you can point the CLI to your custom scenario package with the `modules` argument to `ml scenario` and
`ml db fake`.

---

## Database Schema (High‑Level)

The feature database is defined in `ml.schema` using SQLAlchemy and consists of three main tables:

### `payloads`

Stores the **original inputs**:

- `id` – primary key.
- `payload` – raw payload string (unique).
- `dialect` – textual identifier for the SQL dialect.
- `label` – integer label for classification (e.g. `0` for benign, `1` for malicious).
- `created` – timestamp of ingestion.

Each `payloads` row is linked to one or more rows in `asts` and `lexicals`.

### `asts`

Stores **structured, query‑level features** derived from each payload. At a high level, these include numeric
features related to:

- The number and types of nodes and leaves.
- Presence and counts of different SQL statements and clauses (e.g. `select`, `insert`, `update`, `delete`, `where`,
  `join`, `group` / `order` / `limit`, etc.).
- Aggregate statistics over literals and identifiers (e.g. counts and ratios for certain character classes or
  symbol types).

Each row references `payloads.id` via `payload_id`.

### `lexicals`

Stores **string‑level lexical features** for each payload, such as:

- Overall string length.
- Counts and ratios of digits, letters, uppercase/lowercase, whitespace, and punctuation.
- A general entropy‑like score for the string.
- Counts of specific special characters commonly seen in SQL payloads (e.g. quotes, dash, slash, star, semicolon,
  percent, parentheses, comma, dot, underscore).
- Additional shape/"weirdness" metrics (e.g. repetition, imbalance).

Each row references `payloads.id` via `payload_id`.

> How these features are extracted and used by ML models is **intentionally not documented** here. Only the
> resulting schema is described so you can query or export it for your own experiments.

---

## Typical Workflow

A common end‑to‑end experiment might look like this:

1. **Initialize the database**
   ```bash
   ml db create
   ```

2. **Start the vulnerable SQLi scenario**
   ```bash
   ml scenario
   ```

3. **Collect malicious payloads with external tools**

   In many experiments, malicious samples are generated using external tools such as **sqlmap** against the running
   vulnerable scenario. A typical run will easily produce on the order of **~1500 malicious payloads**.

4. **Generate benign traffic**

   Use the built‑in fake traffic generator to create a larger set of benign requests:

   ```bash
   ml db fake --count 2000
   ```

   As a rule of thumb, aim for the benign dataset size to be **about 500 samples more** than the number of malicious
   payloads produced by tools like sqlmap. For example, if sqlmap produced ~1500 malicious payloads, target **~2000
   benign** requests with `ml db fake` to slightly balance the dataset toward benign traffic.

5. **Optionally add more manual traffic**

   - Send additional benign or malicious payloads manually (e.g. with `curl`, a browser, or custom scripts) against
     the same scenario endpoints.
   - Make sure they are labeled appropriately in your downstream workflow.

6. **Train and evaluate models**

   Connect to the database (using SQLAlchemy, pandas, etc.) and export `payloads`, `asts`, and `lexicals` for ML
   workflows in your own notebooks or scripts.

---

## Safety & Limitations

- The provided scenarios are **deliberately vulnerable** and must never be exposed on the public internet or used
  in production.
- Intended use is **research, experimentation, and coursework** in a controlled environment.
- This README deliberately omits the internal details of how structural and lexical features are derived or how
  classifiers are implemented, to keep the focus on high‑level usage and data flows.
