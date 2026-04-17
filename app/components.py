import streamlit as st
from datetime import date
from calendar import monthrange

from config.settings import BANK_DISPLAY_NAMES, ESG_EMOJIS


def render_sidebar_filters() -> tuple[list[str], list[str], tuple[date, date]]:
    st.sidebar.title("Filtros")

    all_banks = list(BANK_DISPLAY_NAMES.keys())
    all_bank_names = [BANK_DISPLAY_NAMES[b] for b in all_banks]

    selected_bank_names = st.sidebar.multiselect(
        "Bancos",
        options=all_bank_names,
        default=all_bank_names,
        help="Selecione os bancos que deseja visualizar",
    )
    selected_banks = [b for b in all_banks if BANK_DISPLAY_NAMES[b] in selected_bank_names]

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Categoria ESG**")
    esg_options = {"E": "Ambiental", "S": "Social", "G": "Governança"}
    selected_esg = []
    for tag, label in esg_options.items():
        checked = st.sidebar.checkbox(
            f"{ESG_EMOJIS[tag]} {label}",
            value=True,
            key=f"esg_{tag}",
        )
        if checked:
            selected_esg.append(tag)

    st.sidebar.markdown("---")

    current_year = date.today().year

    months_pt = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]

    current = date.today()
    selected_year = st.sidebar.selectbox("Ano", [current_year], index=0)
    selected_month_idx = st.sidebar.selectbox(
        "Mês",
        options=list(range(1, 13)),
        format_func=lambda m: months_pt[m - 1],
        index=current.month - 1,
    )

    month_start = date(selected_year, selected_month_idx, 1)
    last_day = monthrange(selected_year, selected_month_idx)[1]
    month_end = date(selected_year, selected_month_idx, last_day)

    return selected_banks, selected_esg, (month_start, month_end)
