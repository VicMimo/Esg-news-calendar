CREATE TABLE IF NOT EXISTS news (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    data         DATE NOT NULL,
    titulo       TEXT NOT NULL,
    link         TEXT UNIQUE NOT NULL,
    banco_tag    TEXT NOT NULL,
    esg_tag      TEXT NOT NULL,
    resumo       TEXT,
    fonte        TEXT,
    title_hash   TEXT,
    ai_verified  INTEGER DEFAULT 0,
    ai_reasoning TEXT,
    is_fake_flag INTEGER DEFAULT 0,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_data       ON news(data);
CREATE INDEX IF NOT EXISTS idx_banco_tag  ON news(banco_tag);
CREATE INDEX IF NOT EXISTS idx_esg_tag    ON news(esg_tag);
CREATE UNIQUE INDEX IF NOT EXISTS idx_title_hash ON news(title_hash) WHERE title_hash IS NOT NULL;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version    TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
