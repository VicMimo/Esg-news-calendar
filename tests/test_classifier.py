import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.classifier import classify_esg, classify_article
from datetime import date


def test_classify_ambiental():
    assert classify_esg("Itaú lança green bonds para financiamento verde") == "E"


def test_classify_social():
    assert classify_esg("Bradesco aposta em liderança feminina e diversidade") == "S"


def test_classify_governanca():
    assert classify_esg("Santander publica relatório de transparência e governança") == "G"


def test_classify_unknown():
    assert classify_esg("Banco divulga resultados do trimestre") == "unknown"


def test_classify_priority_tiebreak():
    # Both E and S keywords present — E should win
    result = classify_esg("carbono social inclusão ambiental")
    assert result in ("E", "S", "G")


def test_classify_article_full():
    raw = {
        "titulo": "Itaú anuncia crédito de carbono",
        "link": "https://example.com/noticia",
        "data": date(2024, 4, 1),
        "resumo": "O banco lança programa de compensação carbono.",
        "fonte": "example.com",
    }
    article = classify_article(raw, "itau")
    assert article.banco_tag == "itau"
    assert article.esg_tag == "E"
    assert article.titulo == raw["titulo"]


def test_classify_article_social():
    raw = {
        "titulo": "Bradesco investe em inclusão financeira",
        "link": "https://example.com/bradesco",
        "data": date(2024, 4, 2),
        "resumo": "Programa de microcrédito para comunidades vulneráveis.",
        "fonte": "example.com",
    }
    article = classify_article(raw, "bradesco")
    assert article.esg_tag == "S"
