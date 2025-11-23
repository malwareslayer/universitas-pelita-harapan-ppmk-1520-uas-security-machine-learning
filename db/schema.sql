PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS payloads (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  payload TEXT NOT NULL UNIQUE,
  dialect TEXT,
  label   INTEGER,
  error   INTEGER,
  created TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asts (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  payload INTEGER NOT NULL,
  serde   TEXT,   -- Serialized AST

  -- Parse Tree Metrics
  nodes    INTEGER, -- Total Nodes
  leafs    INTEGER, -- Total Nodes Leafs
  trees    INTEGER, -- Tree Depth
  subtrees INTEGER, -- Subtree Depth

  -- Query Metrics
  subqueries INTEGER, -- SELECT ... FROM ... WHERE ... IN (SELECT ... FROM ...)
  selects    INTEGER, -- SELECT ... FROM ...
  inserts    INTEGER, -- INSERT INTO ... VALUES ...
  updates    INTEGER, -- UPDATE ... SET ...
  deletes    INTEGER, -- DELETE FROM ...
  creates    INTEGER, -- CREATE TABLE ...
  drops      INTEGER, -- DROP TABLE ...
  alters     INTEGER, -- ALTER TABLE ...
  wheres     INTEGER, -- ... WHERE ...
  havings    INTEGER, -- ... HAVING ...
  ins        INTEGER, -- ... IN ...

  -- Set Operations Metrics
  unions     INTEGER, -- ... UNION ...
  intersects INTEGER, -- ... INTERSECT ...
  excepts    INTEGER, -- ... EXCEPT ...
  joins      INTEGER, -- ... JOIN ...

  -- Clause Metrics
  limits  INTEGER, -- ... LIMIT 1
  offsets INTEGER, -- ... OFFSET 1
  orders  INTEGER, -- ... ORDER BY ...
  groups  INTEGER, -- ... GROUP BY ...

  -- CTE Metrics
  ctes    INTEGER, -- WITH ... AS ... ... ...
  withs   INTEGER, -- ... AS ... ... ...

  -- Literal Metrics
  literals              INTEGER, -- 'Dwi', 'example@example.com', 123, 3.14
  literal_length        INTEGER, -- Sum All Literal Length
  literal_digits        INTEGER, -- 0123456789
  literal_letters       INTEGER, -- abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
  literal_uppers        INTEGER, -- ABCDEFGHIJKLMNOPQRSTUVWXYZ
  literal_lowers        INTEGER, -- abcdefghijklmnopqrstuvwxyz
  literal_whitespaces   INTEGER, -- Space, Tab, Newline
  literal_specials      INTEGER, -- Non-Alphanumeric & Non-Whitespace
  literal_equals        INTEGER, -- '='
  literal_single_quotes INTEGER, -- '''
  literal_double_quotes INTEGER, -- '"'
  literal_dashes        INTEGER, -- '-'
  literal_slashes       INTEGER, -- '/'
  literal_stars         INTEGER, -- '*'
  literal_semicolons    INTEGER, -- ';'
  literal_percents      INTEGER, -- '%'
  literal_parentheses   INTEGER, -- '(' + ')'
  literal_commas        INTEGER, -- ','
  literal_dots          INTEGER, -- '.'
  literal_underscores   INTEGER, -- '_',
  literal_repeats       INTEGER, -- '))))', '-----'
  literal_imbalances    INTEGER, -- |count('(') - count(')')|

  -- Atomic Metrics
  identifiers           INTEGER, -- Table Name, Column Name

  -- Binaries Metrics
  binaries INTEGER, -- Total Bitwise Operators
  bitors   INTEGER, -- |
  bitands  INTEGER, -- &
  bitxors  INTEGER, -- ^

  -- Arithmetic Metrics
  arithmetics     INTEGER, -- Total Arithmetic Operators
  additions       INTEGER, -- +
  subtractions    INTEGER, -- -
  multiplications INTEGER, -- *
  divisions       INTEGER, -- /
  modulos         INTEGER, -- %

  -- Conditions Metrics
  conditions INTEGER, -- Total Conditions Operators
  eqs        INTEGER, -- =
  neqs       INTEGER, -- !=
  gts        INTEGER, -- >
  lts        INTEGER, -- <
  gtes       INTEGER, -- >=
  ltes       INTEGER, -- <=
  betweens   INTEGER, -- ... BETWEEN ... AND ...
  cases      INTEGER, -- CASE ... WHEN ... THEN ... ELSE ... END

  -- Predicates Metrics
  predicates INTEGER, -- Total Predicates Operators
  ors        INTEGER, -- ... = ... OR ... = ...
  ands       INTEGER, -- ... = ... AND ... = ...
  nots       INTEGER, -- NOT ... = ...

  -- Other Metrics
  functions INTEGER, -- COUNT(), SUM(), AVG()
  comments  INTEGER, -- -- This is a comment

  FOREIGN KEY (payload) REFERENCES payloads(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lexicals (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  payload INTEGER NOT NULL,

  -- Basic counts
  length           INTEGER, -- total chars
  digits           INTEGER, -- 0123456789
  ratio_digits     REAL,
  letters          INTEGER, -- abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
  ratio_letters    REAL,
  uppers           INTEGER, -- ABCDEFGHIJKLMNOPQRSTUVWXYZ
  ratio_upper      REAL,
  lowers           INTEGER, -- abcdefghijklmnopqrstuvwxyz
  ratio_lower      REAL,
  whitespaces      INTEGER, -- Space, Tab, Newline
  ratio_whitespace REAL,
  specials         INTEGER, -- Non-Alphanumeric & Non-Whitespace
  ratio_special    REAL,
  shannon          REAL,

  -- Special Character Counts
  equals        INTEGER, -- '='
  single_quotes INTEGER, -- '''
  double_quotes INTEGER, -- '"'
  dashes        INTEGER, -- '-'
  slashes       INTEGER, -- '/'
  stars         INTEGER, -- '*'
  semicolons    INTEGER, -- ';'
  percents      INTEGER, -- '%'
  parentheses   INTEGER, -- '(' + ')'
  commas        INTEGER, -- ','
  dots          INTEGER, -- '.'
  underscores   INTEGER, -- '_',

  -- Shape / Structural Weirdness
  repeats    INTEGER, -- '))))', '-----'
  imbalances INTEGER, -- |count('(') - count(')')|

  -- Reserved Keywords
  ors      INTEGER,
  ands     INTEGER,
  unions   INTEGER,
  selects  INTEGER,
  inserts  INTEGER,
  updates  INTEGER,
  deletes  INTEGER,
  drops    INTEGER,
  sleeps   INTEGER,
  comments INTEGER,

  FOREIGN KEY (payload) REFERENCES payloads(id) ON DELETE CASCADE
);
