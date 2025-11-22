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

  unions     INTEGER, -- ... UNION ...
  intersects INTEGER, -- ... INTERSECT ...
  excepts    INTEGER, -- ... EXCEPT ...
  joins      INTEGER, -- ... JOIN ...

  limits  INTEGER, -- ... LIMIT 1
  offsets INTEGER, -- ... OFFSET 1
  orders  INTEGER, -- ... ORDER BY ...
  groups  INTEGER, -- ... GROUP BY ...
  ctes    INTEGER, -- WITH ... AS ... ... ...
  withs   INTEGER, -- ... AS ... ... ...

  -- Atomic Metrics
  literals              INTEGER, -- 'Dwi', 'example@example.com', 123, 3.14
  literal_length        INTEGER, -- Sum All Literal Length
  literal_digits        INTEGER,
  literal_letters       INTEGER,
  literal_uppers        INTEGER,
  literal_lowers        INTEGER,
  literal_whitespaces   INTEGER,
  literal_specials      INTEGER,
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

  identifiers           INTEGER, -- Table Name, Column Name

  -- Expressions: Bitwise, Arithmetic
  binaries INTEGER, -- Total Bitwise Operators
  bitors   INTEGER, -- |
  bitands  INTEGER, -- &
  bitxors  INTEGER, -- ^

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
  digits           INTEGER, -- 0-9
  ratio_digits     REAL,
  letters          INTEGER, -- a-zA-Z
  ratio_letters    REAL,
  uppers           INTEGER, -- A-Z
  ratio_upper      REAL,
  lowers           INTEGER, -- a-z
  ratio_lower      REAL,
  whitespaces      INTEGER, -- space, tab, newline
  ratio_whitespace REAL,
  specials         INTEGER, -- non-alnum & non-whitespace
  ratio_special    REAL,
  shannon          REAL,

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
  has_or      INTEGER,
  has_and     INTEGER,
  has_union   INTEGER,
  has_select  INTEGER,
  has_insert  INTEGER,
  has_update  INTEGER,
  has_delete  INTEGER,
  has_drop    INTEGER,
  has_sleep   INTEGER,
  has_comment INTEGER,

  FOREIGN KEY (payload) REFERENCES payloads(id) ON DELETE CASCADE
);
