import calendar
from collections import defaultdict
from datetime import date

import streamlit as st

from config.settings import (
    ESG_COLORS, ESG_EMOJIS, BANK_DISPLAY_NAMES,
    BANK_COLORS, BANK_INITIALS, BANK_MENTION_TERMS,
)

_DAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
_MAX_CARDS_PER_DAY = 3
_MONTHS_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


_dialog = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)


def _render_day_details_body(day_iso: str, articles: list[dict]) -> None:
    try:
        d = date.fromisoformat(day_iso)
        header = f"{d.day} de {_MONTHS_PT[d.month - 1]} de {d.year}"
    except Exception:
        header = day_iso
    st.markdown(f"### {header}")
    st.caption(f"{len(articles)} notícia{'s' if len(articles) != 1 else ''}")
    st.divider()
    for a in articles:
        tag = a.get("esg_tag", "unknown")
        banco_tag = a.get("banco_tag", "")
        banco = BANK_DISPLAY_NAMES.get(banco_tag, banco_tag)
        bank_color = BANK_COLORS.get(banco_tag, "#6c757d")
        esg_color = ESG_COLORS.get(tag, "#6c757d")
        emoji = ESG_EMOJIS.get(tag, "📰")
        titulo = a.get("titulo", "")
        link = a.get("link", "#")
        resumo = a.get("resumo") or ""
        fonte = a.get("fonte") or ""

        fonte_html = f'<span style="opacity:0.6;font-size:0.75rem;">{fonte}</span>' if fonte else ""
        resumo_html = f'<div style="margin-top:6px;font-size:0.85rem;opacity:0.85;">{resumo}</div>' if resumo else ""
        st.markdown(
            f'<div style="border-left:4px solid {bank_color};padding:10px 14px;margin-bottom:12px;'
            f'background:color-mix(in srgb, {bank_color} 6%, transparent);border-radius:6px;">'
            f'<div style="display:flex;gap:8px;align-items:center;margin-bottom:6px;flex-wrap:wrap;">'
            f'<span style="background:{bank_color};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:600;">{banco}</span>'
            f'<span style="background:{esg_color};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.75rem;">{emoji} {tag}</span>'
            f'{fonte_html}'
            f'</div>'
            f'<a href="{link}" target="_blank" style="font-weight:600;font-size:1rem;text-decoration:none;">{titulo}</a>'
            f'{resumo_html}'
            f'</div>',
            unsafe_allow_html=True,
        )


def build_month_grid(year: int, month: int) -> list[list[date | None]]:
    cal = calendar.monthcalendar(year, month)
    return [
        [date(year, month, day) if day != 0 else None for day in week]
        for week in cal
    ]


def _show_day_details(day_iso: str, articles: list[dict]) -> None:
    """Abre modal com todas as notícias do dia (fallback: st.expander se dialog indisponível)."""
    if _dialog is not None:
        @_dialog("Notícias do dia", width="large")
        def _modal():
            _render_day_details_body(day_iso, articles)
        _modal()
    else:
        with st.expander("Notícias do dia", expanded=True):
            _render_day_details_body(day_iso, articles)


def _detect_mentioned_banks(article: dict, primary_tag: str) -> list[str]:
    text = f"{article.get('titulo', '')} {article.get('resumo', '') or ''}".lower()
    mentioned = []
    for tag, terms in BANK_MENTION_TERMS.items():
        if tag == primary_tag:
            continue
        if any(term in text for term in terms):
            mentioned.append(tag)
    return mentioned


def _bank_badge(banco_tag: str, bank_color: str) -> str:
    initials = BANK_INITIALS.get(banco_tag, banco_tag[:2].upper())
    return (
        f'<span style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:18px;height:18px;border-radius:4px;background:{bank_color};'
        f'color:#fff;font-size:0.55rem;font-weight:800;margin-right:5px;'
        f'vertical-align:middle;flex-shrink:0;">{initials}</span>'
    )


def _esg_dots(articles: list[dict]) -> str:
    counts = {"E": 0, "S": 0, "G": 0}
    for a in articles:
        tag = a.get("esg_tag", "unknown")
        if tag in counts:
            counts[tag] += 1
    dots = ""
    for tag, count in counts.items():
        if count > 0:
            color = ESG_COLORS.get(tag, "#6c757d")
            emoji = ESG_EMOJIS.get(tag, "")
            dots += (
                f'<span title="{emoji} {tag}: {count}" style="display:inline-flex;align-items:center;'
                f'justify-content:center;width:16px;height:16px;border-radius:50%;'
                f'background:{color};color:#fff;font-size:0.55rem;font-weight:800;'
                f'margin-left:2px;">{count}</span>'
            )
    return dots


def render_article_card(article: dict) -> str:
    tag = article.get("esg_tag", "unknown")
    banco_tag = article.get("banco_tag", "")
    banco = BANK_DISPLAY_NAMES.get(banco_tag, banco_tag)
    bank_color = BANK_COLORS.get(banco_tag, "#6c757d")
    esg_color = ESG_COLORS.get(tag, "#6c757d")
    emoji = ESG_EMOJIS.get(tag, "📰")

    titulo = article.get("titulo", "")
    if len(titulo) > 70:
        titulo = titulo[:67] + "..."
    link = article.get("link", "#")
    full_title = article.get("titulo", "").replace('"', "&quot;")
    fonte = article.get("fonte") or ""
    if fonte and len(fonte) > 30:
        fonte = fonte[:28] + "…"

    badge = _bank_badge(banco_tag, bank_color)

    mentioned_banks = _detect_mentioned_banks(article, banco_tag)
    extra_badges = ""
    if mentioned_banks:
        extra_badges = '<span style="margin-left:4px;display:inline-flex;gap:2px;align-items:center;">'
        for mb in mentioned_banks:
            mc = BANK_COLORS.get(mb, "#6c757d")
            mn = BANK_DISPLAY_NAMES.get(mb, mb)
            mi = BANK_INITIALS.get(mb, mb[:2].upper())
            extra_badges += (
                f'<span title="Menciona: {mn}" style="display:inline-flex;align-items:center;'
                f'justify-content:center;width:16px;height:16px;border-radius:4px;'
                f'background:{mc};color:#fff;font-size:0.50rem;font-weight:800;'
                f'opacity:0.75;">{mi}</span>'
            )
        extra_badges += '</span>'

    ai_badge = (
        '<span style="font-size:0.55rem;background:rgba(46,125,50,0.2);color:#4caf50;'
        'border-radius:3px;padding:1px 4px;margin-left:4px;">AI✓</span>'
        if article.get("ai_verified") else ""
    )

    fonte_html = f'<div class="card-fonte">{fonte}</div>' if fonte else ""

    return (
        f'<div class="esg-card" style="border-left:4px solid {bank_color};'
        f'background:color-mix(in srgb, {bank_color} 15%, transparent);">'
        f'<div class="card-tag" style="display:flex;align-items:center;flex-wrap:wrap;gap:2px;">'
        f'{badge}'
        f'<span>{banco} · </span>'
        f'<span style="background:{esg_color};color:#fff;border-radius:3px;'
        f'padding:1px 5px;font-size:0.62rem;margin-left:3px;">{emoji} {tag}</span>'
        f'{extra_badges}'
        f'{ai_badge}'
        f'</div>'
        f'<div><a href="{link}" target="_blank" title="{full_title}">{titulo}</a></div>'
        f'{fonte_html}'
        f'</div>'
    )


def render_calendar(articles: list[dict], start: date, end: date = None) -> None:
    by_date: dict[date, list[dict]] = defaultdict(list)
    today = date.today()

    for a in articles:
        d = a.get("data")
        if isinstance(d, str):
            try:
                d = date.fromisoformat(d)
            except ValueError:
                continue
        if d:
            by_date[d].append(a)

    grid = build_month_grid(start.year, start.month)

    header_cols = st.columns(7)
    for i, day_name in enumerate(_DAYS_PT):
        header_cols[i].markdown(
            f'<div class="day-header">{day_name}</div>',
            unsafe_allow_html=True,
        )

    for week in grid:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day is None:
                    st.markdown('<div class="calendar-cell empty-cell"></div>', unsafe_allow_html=True)
                    continue

                is_today = day == today
                is_future = day > today
                day_articles = by_date.get(day, [])

                if is_today:
                    num_class = "day-number today"
                    cell_extra = "today-cell"
                elif is_future:
                    num_class = "day-number future"
                    cell_extra = "future-cell"
                elif not day_articles:
                    num_class = "day-number"
                    cell_extra = "empty-day"
                else:
                    num_class = "day-number"
                    cell_extra = ""

                dots = _esg_dots(day_articles) if day_articles and not is_future else ""
                visible = day_articles[:_MAX_CARDS_PER_DAY]
                hidden_count = len(day_articles) - len(visible)

                html = (
                    f'<div class="calendar-cell {cell_extra}">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
                    f'<div class="esg-dots">{dots}</div>'
                    f'<div class="{num_class}">{day.day}</div>'
                    f'</div>'
                )

                for article in visible:
                    html += render_article_card(article)

                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)

                if day_articles:
                    label = (
                        f"+ {hidden_count} mais · ver dia"
                        if hidden_count > 0
                        else "Ver dia"
                    )
                    if st.button(
                        label,
                        key=f"day_{day.isoformat()}",
                        use_container_width=True,
                    ):
                        _show_day_details(day.isoformat(), day_articles)

    if not articles:
        selected_banks = [a.get("banco_tag") for a in articles]
        st.markdown(
            '<div class="no-data">'
            '📭 Nenhuma notícia encontrada para os filtros selecionados.<br><br>'
            '<span style="font-size:0.85rem;">Tente: ampliar o período, selecionar mais bancos ou categorias ESG.</span>'
            '</div>',
            unsafe_allow_html=True,
        )
