PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS payloads (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  payload BLOB NOT NULL,
  label   INTEGER,
  error   INTEGER,
  created TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asts (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  payload            INTEGER,
  ast                TEXT,
  nodes              INTEGER,
  tree_depths        INTEGER,
  subtree_depths     INTEGER,
  literals           INTEGER,
  identifiers        INTEGER,
  binary_expressions INTEGER,
  comparisons        INTEGER,
  logical_operations INTEGER,
  or_operations      INTEGER,
  and_operations     INTEGER,
  unions             INTEGER,
  comments           INTEGER,
  functions          INTEGER,
  subqueries         INTEGER,
  FOREIGN KEY (payload) REFERENCES payloads(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lexicals (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  payload          INTEGER,
  length           INTEGER,
  digits           INTEGER,
  letters          INTEGER,
  whitespaces      INTEGER,
  specials         INTEGER,
  entropy          REAL,
  ratio_digits     REAL,
  ratio_special    REAL,
  ratio_whitespace REAL,
  FOREIGN KEY (payload) REFERENCES payloads(id) ON DELETE CASCADE
);
