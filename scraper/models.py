from datetime import date
from typing import Literal, Optional

try:
    from pydantic import BaseModel, validator
    PYDANTIC_V2 = False
    try:
        from pydantic import field_validator
        PYDANTIC_V2 = True
    except ImportError:
        pass
except ImportError:
    BaseModel = object

BancoTag = Literal[
    "itau", "bradesco", "santander", "bb", "caixa", "btg",
    "nubank", "safra", "xp", "inter", "c6", "sicoob",
    "bnb", "brb", "original", "pan", "bmg", "agibank", "picpay", "bs2", "bv",
]


def _parse_date(v) -> date:
    if isinstance(v, date):
        return v
    if hasattr(v, "tm_year"):
        return date(v.tm_year, v.tm_mon, v.tm_mday)
    if isinstance(v, str):
        from datetime import datetime
        try:
            return datetime.fromisoformat(v).date()
        except ValueError:
            return datetime.strptime(v[:10], "%Y-%m-%d").date()
    raise ValueError(f"Cannot parse date from {type(v)}: {v!r}")


if PYDANTIC_V2:
    from pydantic import field_validator

    class RawArticle(BaseModel):
        titulo: str
        link: str
        data: date
        resumo: Optional[str] = None
        fonte: Optional[str] = None

        @field_validator("titulo")
        @classmethod
        def titulo_not_empty(cls, v: str) -> str:
            v = v.strip()
            if not v:
                raise ValueError("titulo cannot be empty")
            return v

        @field_validator("data", mode="before")
        @classmethod
        def parse_date(cls, v) -> date:
            return _parse_date(v)

        @field_validator("link", mode="before")
        @classmethod
        def strip_link(cls, v: str) -> str:
            return v.strip()

    class ClassifiedArticle(RawArticle):
        banco_tag: BancoTag
        esg_tag: Literal["E", "S", "G", "unknown"]
        title_hash: Optional[str] = None
        ai_verified: bool = False
        ai_reasoning: Optional[str] = None
        is_fake_flag: bool = False

else:
    from pydantic import BaseModel, validator

    class RawArticle(BaseModel):
        titulo: str
        link: str
        data: date
        resumo: Optional[str] = None
        fonte: Optional[str] = None

        @validator("titulo")
        @classmethod
        def titulo_not_empty(cls, v: str) -> str:
            v = v.strip()
            if not v:
                raise ValueError("titulo cannot be empty")
            return v

        @validator("data", pre=True)
        @classmethod
        def parse_date(cls, v) -> date:
            return _parse_date(v)

        @validator("link", pre=True)
        @classmethod
        def strip_link(cls, v: str) -> str:
            return v.strip()

    class ClassifiedArticle(RawArticle):
        banco_tag: str
        esg_tag: str
        title_hash: Optional[str] = None
        ai_verified: bool = False
        ai_reasoning: Optional[str] = None
        is_fake_flag: bool = False
