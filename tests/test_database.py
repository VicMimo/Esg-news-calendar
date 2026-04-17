import sys
from pathlib import Path
import tempfile
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import initialize_db, insert_article, query_articles, count_articles, get_connection
from scraper.models import ClassifiedArticle
from datetime import date


def make_article(**kwargs) -> ClassifiedArticle:
    defaults = {
        "titulo": "Notícia de teste",
        "link": "https://example.com/test",
        "data": date(2024, 4, 15),
        "banco_tag": "itau",
        "esg_tag": "E",
    }
    defaults.update(kwargs)
    return ClassifiedArticle(**defaults)


def test_initialize_and_insert():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        initialize_db(db_path)
        with get_connection(db_path) as conn:
            article = make_article()
            inserted = insert_article(conn, article)
            assert inserted is True
            assert count_articles(conn) == 1


def test_insert_or_ignore_duplicate():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        initialize_db(db_path)
        with get_connection(db_path) as conn:
            article = make_article()
            insert_article(conn, article)
            inserted_again = insert_article(conn, article)
            assert inserted_again is False
            assert count_articles(conn) == 1


def test_query_articles_filter():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        initialize_db(db_path)
        with get_connection(db_path) as conn:
            insert_article(conn, make_article(link="https://a.com/1", banco_tag="itau", esg_tag="E"))
            insert_article(conn, make_article(link="https://a.com/2", banco_tag="bradesco", esg_tag="S"))
            results = query_articles(conn, date(2024, 4, 1), date(2024, 4, 30), banks=["itau"])
            assert len(results) == 1
            assert results[0]["banco_tag"] == "itau"
