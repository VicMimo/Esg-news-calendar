import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from app.calendar_view import render_calendar
from app.components import render_sidebar_filters, render_month_nav, render_trend_chart, render_ranking
from db.database import get_connection, query_articles, initialize_db, count_articles, count_by_bank, count_by_month_esg
from config.settings import DB_PATH, BANK_DISPLAY_NAMES, BANK_COLORS

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
    initialize_db(DB_PATH)

    with get_connection(DB_PATH) as conn:
        total = count_articles(conn)

    if total == 0:
        st.title("🌱 ESG News Calendar")
        st.warning(
            "Banco de dados vazio. Rode o scraper para buscar as primeiras notícias:\n\n"
            "```\npython -m scraper.pipeline\n```"
        )
        st.stop()

    selected_banks, selected_esg = render_sidebar_filters()
    month_start, month_end = render_month_nav()

    with get_connection(DB_PATH) as conn:
        bank_counts = count_by_bank(
            conn, month_start, month_end,
            banks=selected_banks if selected_banks else None,
            esg_tags=selected_esg if selected_esg else None,
        )

    filtered_total = sum(bank_counts.values())

    st.sidebar.markdown(
        f'<div class="sidebar-metric">'
        f'<div class="sidebar-metric-label">Notícias no período</div>'
        f'<div class="sidebar-metric-value">{filtered_total}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if bank_counts:
        max_count = max(bank_counts.values()) or 1
        st.sidebar.markdown(
            '<div class="sidebar-section-title">Notícias por banco</div>',
            unsafe_allow_html=True,
        )
        for bank in selected_banks or list(BANK_DISPLAY_NAMES.keys()):
            count = bank_counts.get(bank, 0)
            if count > 0:
                color = BANK_COLORS.get(bank, "#6c757d")
                name = BANK_DISPLAY_NAMES.get(bank, bank)
                pct = int(count / max_count * 100)
                st.sidebar.markdown(
                    f'<div class="bank-row">'
                    f'<div class="bank-row-header">'
                    f'<span style="display:flex;align-items:center;gap:6px;">'
                    f'<span style="width:8px;height:8px;border-radius:2px;background:{color};display:inline-block;flex-shrink:0;"></span>'
                    f'<span style="font-size:0.82rem;">{name}</span>'
                    f'</span>'
                    f'<span style="font-weight:800;font-size:0.82rem;color:{color};">{count}</span>'
                    f'</div>'
                    f'<div class="bank-bar-track">'
                    f'<div class="bank-bar-fill" style="width:{pct}%;background:{color};"></div>'
                    f'</div>'
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
            monthly = count_by_month_esg(
                conn,
                months_back=6,
                banks=selected_banks if selected_banks else None,
            )

    render_ranking(bank_counts, top_n=3)
    render_calendar(articles, month_start, month_end)
    render_trend_chart(monthly)


if __name__ == "__main__":
    main()
