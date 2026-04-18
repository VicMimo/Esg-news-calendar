import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import date

from app.calendar_view import render_calendar
from app.components import render_sidebar_filters, render_search_bar, render_month_nav
from db.database import get_connection, query_articles, initialize_db, count_articles, count_by_bank
from config.settings import DB_PATH

st.set_page_config(
    page_title="ESG News Calendar",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).parent / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def main():
    st.title("🌱 ESG News Calendar — Bancos Brasileiros")
    st.caption("Rastreamento diário de ações ESG dos principais bancos do Brasil")

    initialize_db(DB_PATH)

    with get_connection(DB_PATH) as conn:
        total = count_articles(conn)

    if total == 0:
        st.warning(
            "Banco de dados vazio. Rode o scraper para buscar as primeiras notícias:\n\n"
            "```\npython -m scraper.pipeline\n```"
        )
        st.stop()

    st.sidebar.metric("Total de notícias", total)

    selected_banks, selected_esg = render_sidebar_filters()

    search_query = render_search_bar()
    month_start, month_end = render_month_nav()

    from config.settings import BANK_DISPLAY_NAMES, BANK_COLORS
    with get_connection(DB_PATH) as conn:
        bank_counts = count_by_bank(
            conn, month_start, month_end,
            banks=selected_banks if selected_banks else None,
            esg_tags=selected_esg if selected_esg else None,
        )

    filtered_total = sum(bank_counts.values())
    st.sidebar.metric("Notícias no período", filtered_total)

    if bank_counts:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Notícias por banco**")
        for bank in selected_banks or list(BANK_DISPLAY_NAMES.keys()):
            count = bank_counts.get(bank, 0)
            if count > 0:
                color = BANK_COLORS.get(bank, "#6c757d")
                name = BANK_DISPLAY_NAMES.get(bank, bank)
                st.sidebar.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'padding:3px 0;font-size:0.85rem;">'
                    f'<span style="display:flex;align-items:center;gap:6px;">'
                    f'<span style="width:10px;height:10px;border-radius:2px;background:{color};display:inline-block;"></span>'
                    f'{name}</span>'
                    f'<span style="font-weight:700;color:{color};">{count}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with st.spinner("Carregando notícias..."):
        with get_connection(DB_PATH) as conn:
            articles = query_articles(
                conn,
                start_date=month_start,
                end_date=month_end,
                banks=selected_banks if selected_banks else None,
                esg_tags=selected_esg if selected_esg else None,
            )

    if search_query:
        articles = [
            a for a in articles
            if search_query in (a.get("titulo") or "").lower()
            or search_query in (a.get("resumo") or "").lower()
        ]

    if search_query:
        st.caption(f'Busca: "{search_query}" — {len(articles)} resultado{"s" if len(articles) != 1 else ""}')

    render_calendar(articles, month_start, month_end)


if __name__ == "__main__":
    main()
