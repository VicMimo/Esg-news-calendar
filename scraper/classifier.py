from config.settings import ESG_KEYWORDS
from scraper.models import ClassifiedArticle, RawArticle


def classify_esg(text: str, keyword_map: dict = None) -> str:
    if keyword_map is None:
        keyword_map = ESG_KEYWORDS
    text_lower = text.lower()
    scores = {cat: 0 for cat in keyword_map}
    for cat, keywords in keyword_map.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[cat] += 1
    best_score = max(scores.values())
    if best_score == 0:
        return "unknown"
    # Priority tiebreak: E > S > G
    for cat in ("E", "S", "G"):
        if scores[cat] == best_score:
            return cat
    return "unknown"


def classify_article(raw: dict, banco_tag: str) -> ClassifiedArticle:
    text = f"{raw.get('titulo', '')} {raw.get('resumo', '') or ''}"
    esg_tag = classify_esg(text)
    return ClassifiedArticle(
        titulo=raw["titulo"],
        link=raw["link"],
        data=raw["data"],
        resumo=raw.get("resumo"),
        fonte=raw.get("fonte"),
        banco_tag=banco_tag,
        esg_tag=esg_tag,
    )
