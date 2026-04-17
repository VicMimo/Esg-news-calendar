import hashlib
import re
import unicodedata
from datetime import date


def normalize_title(titulo: str) -> str:
    titulo = unicodedata.normalize("NFKD", titulo.lower())
    titulo = titulo.encode("ascii", "ignore").decode("ascii")
    titulo = re.sub(r"[^\w\s]", "", titulo)
    words = titulo.split()[:20]
    return " ".join(words)


def compute_title_hash(titulo: str, pub_date: date) -> str:
    normalized = normalize_title(titulo)
    payload = f"{normalized}|{pub_date.isoformat()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
