from config.settings import ESG_KEYWORDS
from scraper.models import ClassifiedArticle, RawArticle


TITLE_BLACKLIST = [
    "patrocínio", "patrocinio", "patrocina",
    "futebol", "libertadores", "brasileirão", "brasileirao", "campeonato",
    "cotação", "cotacao", "cotações", "cotacoes",
    "dividendo", "dividendos", "jcp", "juros sobre capital",
    "lucro líquido", "lucro liquido", "balanço trimestral", "balanco trimestral",
    "resultado trimestral", "receita trimestral", "ebitda",
    "ação sobe", "acao sobe", "ação cai", "acao cai", "ações sobem", "ações caem",
    "bolsa fecha", "ibovespa", "dólar fecha", "dolar fecha",
    "fusão", "fusao", "aquisição hostil", "aquisicao hostil",
    "ipo", "oferta pública", "oferta publica",
    "reclame aqui", "golpe", "fraude", "vazamento de dados",
    "demissão", "demissao", "demissões", "demissoes", "corte de vagas",
    "processo judicial", "multa do procon", "multa do bacen",
]


def is_noise(text: str, blacklist: list = None) -> bool:
    if blacklist is None:
        blacklist = TITLE_BLACKLIST
    text_lower = text.lower()
    for term in blacklist:
        if term in text_lower:
            return True
    return False


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
