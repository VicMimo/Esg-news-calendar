import calendar
from collections import defaultdict
from datetime import date

import streamlit as st

from config.settings import (
    ESG_COLORS, ESG_EMOJIS, BANK_DISPLAY_NAMES,
    BANK_COLORS, BANK_INITIALS,
)

_DAYS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def build_month_grid(year: int, month: int) -> list[list[date | None]]:
    cal = calendar.monthcalendar(year, month)
    return [
        [date(year, month, day) if day != 0 else None for day in week]
        for week in cal
    ]


def _bank_badge(banco_tag: str, bank_color: str) -> str:
    initials = BANK_INITIALS.get(banco_tag, banco_tag[:2].upper())
    return (
        f'<span style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:18px;height:18px;border-radius:4px;background:{bank_color};'
        f'color:#fff;font-size:0.55rem;font-weight:800;margin-right:5px;'
        f'vertical-align:middle;flex-shrink:0;">{initials}</span>'
    )


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

    ai_badge = (
        '<span style="font-size:0.55rem;background:rgba(46,125,50,0.2);color:#4caf50;'
        'border-radius:3px;padding:1px 4px;margin-left:4px;">AI✓</span>'
        if article.get("ai_verified") else ""
    )

    fonte_html = (
        f'<div class="card-fonte">{fonte}</div>' if fonte else ""
    )

    return (
        f'<div class="esg-card" style="border-left:4px solid {bank_color};'
        f'background:color-mix(in srgb, {bank_color} 15%, transparent);">'
        f'<div class="card-tag" style="display:flex;align-items:center;">'
        f'{badge}'
        f'<span>{banco} · </span>'
        f'<span style="background:{esg_color};color:#fff;border-radius:3px;'
        f'padding:1px 5px;font-size:0.62rem;margin-left:3px;">{emoji} {tag}</span>'
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
        if d and d != today or d == today:
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
                elif is_future:
                    num_class = "day-number future"
                else:
                    num_class = "day-number"

                cell_class = "calendar-cell"
                if is_future:
                    cell_class += " future-cell"
                elif not day_articles:
                    cell_class += " empty-day"

                html = f'<div class="{cell_class}"><div class="{num_class}">{day.day}</div>'
                for article in day_articles:
                    html += render_article_card(article)
                html += "</div>"

                st.markdown(html, unsafe_allow_html=True)

    if not articles:
        st.markdown(
            '<div class="no-data">Nenhuma notícia encontrada para os filtros selecionados.</div>',
            unsafe_allow_html=True,
        )
