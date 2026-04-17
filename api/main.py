import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from datetime import date
from calendar import monthrange

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from db.database import get_connection, query_articles_json, get_date_range, count_articles
from config.settings import DB_PATH, BANK_DISPLAY_NAMES, BANK_COLORS, BANK_INITIALS
from api.embed import build_embed_html

app = FastAPI(
    title="ESG News API",
    description="API de notícias ESG dos principais bancos brasileiros",
    version="2.0.0",
)

# CORS: aceita apenas origens configuradas via variável de ambiente.
# Defina ALLOWED_ORIGINS no .env separando por vírgula, ex:
#   ALLOWED_ORIGINS=https://empresa.sharepoint.com,https://empresa.com
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)

_VALID_BANKS = set(BANK_DISPLAY_NAMES.keys())
_VALID_ESG = {"E", "S", "G", "unknown"}


@app.get("/api/news", summary="Listar notícias ESG")
def get_news(
    start_date: date = Query(default=None, description="Data inicial (YYYY-MM-DD)"),
    end_date: date = Query(default=None, description="Data final (YYYY-MM-DD)"),
    banks: list[str] = Query(default=None, description="Tags dos bancos (ex: itau, bradesco)"),
    esg_tags: list[str] = Query(default=None, description="Categorias ESG (E, S, G)"),
    limit: int = Query(default=100, ge=1, le=500, description="Máximo de resultados"),
) -> dict:
    today = date.today()
    if start_date is None:
        start_date = date(today.year, today.month, 1)
    if end_date is None:
        end_date = date(today.year, today.month, monthrange(today.year, today.month)[1])

    if banks:
        invalid = [b for b in banks if b not in _VALID_BANKS]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Bancos inválidos: {invalid}")

    if esg_tags:
        invalid = [t for t in esg_tags if t not in _VALID_ESG]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Categorias ESG inválidas: {invalid}")

    with get_connection(DB_PATH) as conn:
        articles = query_articles_json(conn, start_date, end_date, banks, esg_tags, limit)

    return {
        "count": len(articles),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "articles": articles,
    }


@app.get("/api/banks", summary="Listar bancos disponíveis")
def get_banks() -> dict:
    return {
        "banks": [
            {
                "tag": tag,
                "name": name,
                "color": BANK_COLORS.get(tag, "#6c757d"),
                "initials": BANK_INITIALS.get(tag, tag[:2].upper()),
            }
            for tag, name in BANK_DISPLAY_NAMES.items()
        ]
    }


@app.get("/api/stats", summary="Estatísticas do banco de dados")
def get_stats() -> dict:
    with get_connection(DB_PATH) as conn:
        total = count_articles(conn)
        min_date, max_date = get_date_range(conn)
    return {
        "total_articles": total,
        "earliest_date": min_date.isoformat(),
        "latest_date": max_date.isoformat(),
    }


@app.get("/embed", response_class=HTMLResponse, summary="Calendário HTML para SharePoint iFrame")
def embed_calendar(
    banks: list[str] = Query(default=None),
    esg_tags: list[str] = Query(default=None),
    month: int = Query(default=None, ge=1, le=12),
    year: int = Query(default=None, ge=2000, le=2099),
) -> str:
    today = date.today()
    y = year or today.year
    m = month or today.month
    try:
        start = date(y, m, 1)
        end = date(y, m, monthrange(y, m)[1])
    except ValueError:
        raise HTTPException(status_code=400, detail="Data inválida")

    if banks:
        banks = [b for b in banks if b in _VALID_BANKS]
    if esg_tags:
        esg_tags = [t for t in esg_tags if t in _VALID_ESG]

    with get_connection(DB_PATH) as conn:
        articles = query_articles_json(conn, start, end, banks or None, esg_tags or None, limit=500)

    return build_embed_html(articles)


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """<html><body style="font-family:sans-serif;padding:40px;">
    <h1>🌱 ESG News API</h1>
    <p>Endpoints disponíveis:</p>
    <ul>
      <li><a href="/api/news">/api/news</a> — notícias ESG (JSON)</li>
      <li><a href="/api/banks">/api/banks</a> — bancos e cores</li>
      <li><a href="/api/stats">/api/stats</a> — estatísticas</li>
      <li><a href="/embed">/embed</a> — calendário HTML (SharePoint iFrame)</li>
      <li><a href="/docs">/docs</a> — documentação Swagger</li>
    </ul>
    </body></html>"""
