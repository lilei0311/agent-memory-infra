-- Synthetic OpenClaw-shaped memory index.
-- Invented text. Not a user database. Contains no secrets.
-- Observations live in memory_index_chunks.text.
-- memory_index_sources is provenance only.

PRAGMA page_size = 512;

CREATE TABLE memory_index_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE memory_index_sources (
  path TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'memory',
  hash TEXT NOT NULL,
  mtime INTEGER NOT NULL,
  size INTEGER NOT NULL,
  PRIMARY KEY (path, source)
);

CREATE TABLE memory_index_chunks (
  id TEXT PRIMARY KEY,
  path TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'memory',
  start_line INTEGER NOT NULL,
  end_line INTEGER NOT NULL,
  hash TEXT NOT NULL,
  model TEXT NOT NULL,
  text TEXT NOT NULL,
  embedding TEXT NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX idx_memory_index_sources_source ON memory_index_sources(source);
CREATE INDEX idx_memory_index_chunks_path_source ON memory_index_chunks(path, source);
CREATE INDEX idx_memory_index_chunks_path ON memory_index_chunks(path);
CREATE INDEX idx_memory_index_chunks_source ON memory_index_chunks(source);

INSERT INTO memory_index_meta (key, value) VALUES ('fixture', 'synthetic');

INSERT INTO memory_index_sources (path, source, hash, mtime, size) VALUES
  ('MEMORY.md', 'memory', 'mem-hash', 1700000000, 120),
  ('memory/synthetic.md', 'memory', 'syn-hash', 1700000001, 80),
  ('sessions/demo.jsonl', 'sessions', 'ses-hash', 1700000002, 40);

INSERT INTO memory_index_chunks (
  id, path, source, start_line, end_line, hash, model, text, embedding, updated_at
) VALUES
  (
    'c1', 'MEMORY.md', 'memory', 1, 1, 'c1-hash', 'synthetic-embedder',
    'The workspace prefers explicit confirmation before import.', '[]', 1700000100
  ),
  (
    'c2', 'MEMORY.md', 'memory', 2, 2, 'c2-hash', 'synthetic-embedder',
    'the workspace prefers explicit confirmation before import.', '[]', 1700000101
  ),
  (
    'c3', 'memory/synthetic.md', 'memory', 4, 4, 'c3-hash', 'synthetic-embedder',
    'SQLite fixture: the index is read and never rewritten.', '[]', 1700000102
  ),
  (
    'c5', 'memory/synthetic.md', 'memory', 8, 8, 'c5-hash', 'synthetic-embedder',
    '   ', '[]', 1700000103
  ),
  (
    'c6', 'notes/extra.md', 'memory', 1, 1, 'c6-hash', 'synthetic-embedder',
    'Unique sqlite fact: fixtures are checked in on purpose.', '[]', 1700000104
  ),
  (
    'c4', 'sessions/demo.jsonl', 'sessions', 3, 3, 'c4-hash', 'synthetic-embedder',
    'Session chunk: standup notes live in the team channel.', '[]', 1700000105
  );
