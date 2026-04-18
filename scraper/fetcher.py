import logging
import time
import random
from datetime import date
from urllib.parse import urlencode, urlparse

import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_USER_AGENT = "Mozilla/5.0 (compatible; ESGNewsBot/1.0)"

# Títulos que contenham qualquer um desses termos são descartados como ruído
_NOISE_TERMS = [
    "portal salário", "salário", "vaga de emprego", "operador de caixa",
    "auxiliar", "assistente", "analista junior", "trainee", "estágio",
    "recrutamento", "processo seletivo", "currículo", "indeed.com",
    "catho", "infojobs", "linkedin vagas", "glassdoor",
    # Safra agrícola (não banco)
    "safra de", "safra 202", "safra brasileira", "safra de milho",
    "safra de soja", "safra de cana", "safra de café", "safra de trigo",
    "safra de arroz", "safrinha", "supersafra", "nova safra",
    "próxima safra", "estimativa de safra", "produção de safra",
    # Inter (ambíguo)
    "inter miami", "inter de milão", "internazionale",
]


def build_google_news_url(query: str, lang: str = "pt", country: str = "BR") -> str:
    params = urlencode({
        "q": query,
        "hl": f"{lang}-{country}",
        "gl": country,
        "ceid": f"{country}:{lang}",
    })
    return f"https://news.google.com/rss/search?{params}"


def _clean_html(text: str | None) -> str | None:
    if not text:
        return None
    return BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)


def _extract_fonte(link: str) -> str | None:
    try:
        netloc = urlparse(link).netloc.lower()
        return netloc.removeprefix("www.")
    except Exception:
        return None


def is_trusted_source(fonte: str | None, trusted_domains: set) -> bool:
    if not fonte:
        return False
    fonte = fonte.lower().removeprefix("www.")
    # Rejeita explicitamente agregadores/redirecionadores
    if fonte in ("news.google.com", "google.com", "yahoo.com", "bing.com"):
        return False
    parts = fonte.split(".")
    for i in range(len(parts)):
        candidate = ".".join(parts[i:])
        if candidate in trusted_domains:
            return True
    return False


def _parse_entry(entry: dict) -> dict | None:
    try:
        titulo = entry.get("title", "").strip()
        if not titulo:
            return None

        link = entry.get("link", "").strip()
        if not link:
            return None

        published = entry.get("published_parsed") or entry.get("updated_parsed")
        pub_date = (
            date(published.tm_year, published.tm_mon, published.tm_mday)
            if published
            else date.today()
        )

        resumo_raw = entry.get("summary") or entry.get("description")
        resumo = _clean_html(resumo_raw)
        if resumo and len(resumo) > 500:
            resumo = resumo[:497] + "..."

        # Google News RSS wraps links — real source domain is in entry['source']['href']
        source_info = entry.get("source") or {}
        source_href = source_info.get("href", "") if isinstance(source_info, dict) else ""
        fonte = _extract_fonte(source_href) if source_href else _extract_fonte(link)

        return {
            "titulo": titulo,
            "link": link,
            "data": pub_date,
            "resumo": resumo,
            "fonte": fonte,
        }
    except Exception as e:
        logger.warning(f"Failed to parse entry: {e}")
        return None


def fetch_feed(url: str, max_retries: int = 3) -> list[dict]:
    for attempt in range(max_retries):
        try:
            feed = feedparser.parse(
                url,
                agent=_USER_AGENT,
                request_headers={"Accept-Language": "pt-BR,pt;q=0.9"},
            )
            if feed.bozo and not feed.entries:
                wait = 2 ** attempt
                logger.warning(
                    f"Feed error (attempt {attempt + 1}): {feed.bozo_exception}. "
                    f"Retrying in {wait}s"
                )
                time.sleep(wait)
                continue
            return feed.entries
        except Exception as e:
            logger.warning(f"Fetch exception (attempt {attempt + 1}): {e}")
            time.sleep(2 ** attempt)
    return []


def fetch_all_banks(
    bank_queries: dict,
    delay_seconds: float = 2.5,
    max_articles_per_query: int = 20,
    trusted_domains: set | None = None,
) -> list[tuple[str, list[dict]]]:
    results = []
    total_queries = sum(len(q) for q in bank_queries.values())
    done = 0

    for banco_tag, queries in bank_queries.items():
        for query in queries:
            url = build_google_news_url(query)
            logger.info(f"Fetching [{banco_tag}] '{query}'")
            try:
                entries = fetch_feed(url)
                parsed = []
                for entry in entries[:max_articles_per_query]:
                    p = _parse_entry(entry)
                    if not p:
                        continue
                    if trusted_domains and not is_trusted_source(p.get("fonte"), trusted_domains):
                        continue
                    titulo_lower = p["titulo"].lower()
                    if any(noise in titulo_lower for noise in _NOISE_TERMS):
                        logger.debug(f"[NOISE] {p['titulo'][:60]}")
                        continue
                    parsed.append(p)
                results.append((banco_tag, parsed))
                logger.info(f"  >> {len(parsed)} articles accepted")
            except Exception as e:
                logger.error(f"Failed to fetch '{query}': {e}")
                results.append((banco_tag, []))

            done += 1
            if done < total_queries:
                jitter = random.uniform(0, 1.5)
                time.sleep(delay_seconds + jitter)

    return results
