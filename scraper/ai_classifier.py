import json
import logging
import os

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Você é um especialista em ESG (Environmental, Social, Governance) "
    "para o setor financeiro brasileiro. Analise o artigo fornecido e "
    "responda SOMENTE com JSON válido, sem texto adicional."
)

_USER_TEMPLATE = """Título: {titulo}
Resumo: {resumo}
Banco identificado: {banco}
Classificação prévia por palavras-chave: {keyword_tag}

Responda SOMENTE com este JSON:
{{
  "is_esg_related": true ou false,
  "esg_tag": "E" ou "S" ou "G" ou "unknown",
  "reasoning": "explicação em até 150 caracteres",
  "is_fake_or_noise": true ou false
}}

Critérios:
- is_esg_related: true apenas se a notícia reporta uma ação ESG CONCRETA do banco (não menção genérica)
- is_fake_or_noise: true se parece agregador, spam, conteúdo gerado, ou sem relação real com ESG do banco
"""

_FALLBACK = {
    "is_esg_related": True,
    "esg_tag": None,
    "reasoning": "fallback (IA não disponível)",
    "is_fake_or_noise": False,
}


def _get_azure_client():
    try:
        from openai import AzureOpenAI
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
        key = os.environ.get("AZURE_OPENAI_KEY", "")
        if not endpoint or not key:
            return None, None
        deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=key,
            api_version="2024-02-01",
        )
        return client, deployment
    except ImportError:
        return None, None


def verify_and_classify(
    titulo: str,
    resumo: str | None,
    banco_tag: str,
    keyword_esg_tag: str,
) -> dict:
    """
    Returns dict with: is_esg_related, esg_tag, reasoning, is_fake_or_noise.
    Falls back to keyword result when Azure OpenAI is not configured.
    """
    client, deployment = _get_azure_client()
    if client is None:
        fallback = dict(_FALLBACK)
        fallback["esg_tag"] = keyword_esg_tag
        return fallback

    prompt = _USER_TEMPLATE.format(
        titulo=titulo,
        resumo=resumo or "N/A",
        banco=banco_tag,
        keyword_tag=keyword_esg_tag,
    )
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=250,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        if "esg_tag" not in result or result["esg_tag"] not in ("E", "S", "G", "unknown"):
            result["esg_tag"] = keyword_esg_tag
        return result
    except Exception as e:
        logger.warning(f"Azure OpenAI call failed, using keyword fallback: {e}")
        fallback = dict(_FALLBACK)
        fallback["esg_tag"] = keyword_esg_tag
        return fallback


def is_ai_available() -> bool:
    return bool(
        os.environ.get("AZURE_OPENAI_ENDPOINT")
        and os.environ.get("AZURE_OPENAI_KEY")
    )
