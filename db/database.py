import sqlite3
import logging
from contextlib import contextmanager
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

_MIGRATIONS_DIR = Path(__file__).parent / "migrations"


@contextmanager
def get_connection(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _run_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations "
        "(version TEXT PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    applied = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}

    if not _MIGRATIONS_DIR.exists():
        return

    for migration_file in sorted(_MIGRATIONS_DIR.glob("*.sql")):
        version = migration_file.stem
        if version in applied:
            continue
        sql = migration_file.read_text(encoding="utf-8")
        for statement in sql.split(";"):
            stmt = statement.strip()
            if stmt:
                try:
                    conn.execute(stmt)
                except sqlite3.OperationalError as e:
                    # Ignore "duplicate column" errors from idempotent migrations
                    if "duplicate column" not in str(e).lower():
                        raise
        conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
        logger.info(f"Applied migration: {version}")


def initialize_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path = Path(__file__).parent / "schema.sql"
    # executescript issues an implicit COMMIT, so use a raw connection here.
    # Run migrations FIRST (ALTER TABLE to add new columns), then apply the
    # full schema script so any new indexes on those columns succeed.
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        # Bootstrap the base table without new indexes (safe for existing DBs)
        base_ddl = """
        CREATE TABLE IF NOT EXISTS news (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            data       DATE NOT NULL,
            titulo     TEXT NOT NULL,
            link       TEXT UNIQUE NOT NULL,
            banco_tag  TEXT NOT NULL,
            esg_tag    TEXT NOT NULL,
            resumo     TEXT,
            fonte      TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_data      ON news(data);
        CREATE INDEX IF NOT EXISTS idx_banco_tag ON news(banco_tag);
        CREATE INDEX IF NOT EXISTS idx_esg_tag   ON news(esg_tag);
        """
        conn.executescript(base_ddl)
        # Apply ALTER TABLE migrations (adds new columns if not present)
        _run_migrations(conn)
        # Now apply the full schema (new indexes on already-existing columns)
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()
    logger.info(f"Database initialized at {db_path}")


def title_hash_exists(conn: sqlite3.Connection, title_hash: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM news WHERE title_hash = ? LIMIT 1", (title_hash,)
    ).fetchone()
    return row is not None


def insert_article(conn: sqlite3.Connection, article) -> bool:
    title_hash = getattr(article, "title_hash", None)
    if title_hash and title_hash_exists(conn, title_hash):
        return False

    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO news
            (data, titulo, link, banco_tag, esg_tag, resumo, fonte,
             title_hash, ai_verified, ai_reasoning, is_fake_flag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(article.data),
            article.titulo,
            article.link,
            article.banco_tag,
            article.esg_tag,
            article.resumo,
            article.fonte,
            title_hash,
            int(getattr(article, "ai_verified", False)),
            getattr(article, "ai_reasoning", None),
            int(getattr(article, "is_fake_flag", False)),
        ),
    )
    return cursor.rowcount > 0


def query_articles(
    conn: sqlite3.Connection,
    start_date: date,
    end_date: date,
    banks: list[str] | None = None,
    esg_tags: list[str] | None = None,
) -> list[dict]:
    sql = "SELECT * FROM news WHERE data BETWEEN ? AND ? AND is_fake_flag = 0"
    params: list = [str(start_date), str(end_date)]

    if banks:
        placeholders = ",".join("?" * len(banks))
        sql += f" AND banco_tag IN ({placeholders})"
        params.extend(banks)

    if esg_tags:
        placeholders = ",".join("?" * len(esg_tags))
        sql += f" AND esg_tag IN ({placeholders})"
        params.extend(esg_tags)

    sql += " ORDER BY data DESC, created_at DESC"
    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def query_articles_json(
    conn: sqlite3.Connection,
    start_date: date,
    end_date: date,
    banks: list[str] | None = None,
    esg_tags: list[str] | None = None,
    limit: int = 500,
) -> list[dict]:
    from config.settings import BANK_DISPLAY_NAMES, ESG_LABELS
    rows = query_articles(conn, start_date, end_date, banks, esg_tags)[:limit]
    result = []
    for row in rows:
        r = dict(row)
        r["banco_display"] = BANK_DISPLAY_NAMES.get(r.get("banco_tag", ""), r.get("banco_tag", ""))
        r["esg_label"] = ESG_LABELS.get(r.get("esg_tag", ""), r.get("esg_tag", ""))
        r["ai_verified"] = bool(r.get("ai_verified", 0))
        r["is_fake_flag"] = bool(r.get("is_fake_flag", 0))
        result.append(r)
    return result


def get_date_range(conn: sqlite3.Connection) -> tuple[date, date]:
    row = conn.execute("SELECT MIN(data), MAX(data) FROM news").fetchone()
    if row[0] is None:
        today = date.today()
        return today, today
    return (
        date.fromisoformat(row[0]),
        date.fromisoformat(row[1]),
    )


def count_articles(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM news").fetchone()[0]
