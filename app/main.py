import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import date

from app.calendar_view import render_calendar
from app.components import render_sidebar_filters
from db.database import get_connection, query_articles, initialize_db, count_articles
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

    selected_banks, selected_esg, (month_start, month_end) = render_sidebar_filters()

    with get_connection(DB_PATH) as conn:
        articles = query_articles(
            conn,
            start_date=month_start,
            end_date=month_end,
            banks=selected_banks if selected_banks else None,
            esg_tags=selected_esg if selected_esg else None,
        )

    months_pt = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]
    st.subheader(f"{months_pt[month_start.month - 1]} {month_start.year} — {len(articles)} notícias")

    render_calendar(articles, month_start, month_end)


if __name__ == "__main__":
    main()
