import streamlit as st
from datetime import date
from calendar import monthrange

from config.settings import BANK_DISPLAY_NAMES, ESG_EMOJIS


def render_month_nav() -> tuple[date, date]:
    today = date.today()

    if "nav_year" not in st.session_state:
        st.session_state.nav_year = today.year
    if "nav_month" not in st.session_state:
        st.session_state.nav_month = today.month

    months_pt = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]

    year = st.session_state.nav_year
    month = st.session_state.nav_month

    # Limits: Jan of current year ↔ current month
    at_min = (year == today.year and month == 1)
    at_max = (year == today.year and month == today.month)

    col_prev, col_label, col_next = st.columns([1, 4, 1])

    with col_prev:
        if st.button("◀", disabled=at_min, use_container_width=True, key="nav_prev"):
            if month == 1:
                st.session_state.nav_month = 12
                st.session_state.nav_year = year - 1
            else:
                st.session_state.nav_month = month - 1
            st.rerun()

    with col_label:
        with st.popover(
            f"{months_pt[month - 1]} {year}",
            use_container_width=True,
        ):
            st.markdown("**Ir para mês/ano**")
            available_years = list(range(today.year, today.year + 1))
            sel_year = st.selectbox("Ano", available_years, index=0, key="pop_year")
            max_month = today.month if sel_year == today.year else 12
            sel_month = st.selectbox(
                "Mês",
                list(range(1, max_month + 1)),
                format_func=lambda m: months_pt[m - 1],
                index=max_month - 1,
                key="pop_month",
            )
            if st.button("Ir", use_container_width=True, key="pop_go"):
                st.session_state.nav_year = sel_year
                st.session_state.nav_month = sel_month
                st.rerun()

    with col_next:
        if st.button("▶", disabled=at_max, use_container_width=True, key="nav_next"):
            if month == 12:
                st.session_state.nav_month = 1
                st.session_state.nav_year = year + 1
            else:
                st.session_state.nav_month = month + 1
            st.rerun()

    month_start = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    month_end = date(year, month, last_day)

    return month_start, month_end


def render_sidebar_filters() -> tuple[list[str], list[str]]:
    from config.settings import ESG_COLORS

    st.sidebar.markdown(
        '<div style="font-size:1.1rem;font-weight:800;padding:8px 0 4px;">Filtros</div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<div class="sidebar-section-title">Bancos</div>',
        unsafe_allow_html=True,
    )

    all_banks = list(BANK_DISPLAY_NAMES.keys())
    all_bank_names = [BANK_DISPLAY_NAMES[b] for b in all_banks]

    selected_bank_names = st.sidebar.multiselect(
        "Bancos",
        options=all_bank_names,
        default=all_bank_names,
        label_visibility="collapsed",
    )
    selected_banks = [b for b in all_banks if BANK_DISPLAY_NAMES[b] in selected_bank_names]

    st.sidebar.markdown(
        '<div class="sidebar-section-title">Categoria ESG</div>',
        unsafe_allow_html=True,
    )

    esg_options = {"E": ("Ambiental", "#2d6a4f"), "S": ("Social", "#1d3557"), "G": ("Governança", "#6a0572")}
    selected_esg = []
    for tag, (label, color) in esg_options.items():
        emoji = ESG_EMOJIS[tag]
        checked = st.sidebar.checkbox(
            f"{emoji} {label}",
            value=True,
            key=f"esg_{tag}",
        )
        if checked:
            selected_esg.append(tag)

    return selected_banks, selected_esg
