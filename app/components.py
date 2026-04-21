import streamlit as st
from datetime import date
from calendar import monthrange

from config.settings import BANK_DISPLAY_NAMES, ESG_EMOJIS

MONTHS_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def render_month_nav() -> tuple[date, date]:
    today = date.today()

    if "nav_year" not in st.session_state:
        st.session_state.nav_year = today.year
    if "nav_month" not in st.session_state:
        st.session_state.nav_month = today.month

    year = st.session_state.nav_year
    month = st.session_state.nav_month

    at_min = (year == today.year and month == 1)
    at_max = (year == today.year and month == today.month)

    # Navigation rendered in main body
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
            f"{MONTHS_PT[month - 1]} {year}",
            use_container_width=True,
        ):
            st.markdown("**Ir para mês/ano**")
            available_years = [today.year]
            sel_year = st.selectbox("Ano", available_years, index=0, key="pop_year")
            max_month = today.month if sel_year == today.year else 12
            sel_month = st.selectbox(
                "Mês",
                list(range(1, max_month + 1)),
                format_func=lambda m: MONTHS_PT[m - 1],
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
    st.sidebar.markdown(
        '<div style="padding:4px 0 12px;">'
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
        '<span style="font-size:1.6rem;line-height:1;">🌱</span>'
        '<span style="font-size:1.2rem;font-weight:800;">ESG News Calendar</span>'
        '</div>'
        '<div style="font-size:0.78rem;color:#6c757d;line-height:1.5;">'
        'Rastreamento diário de notícias ambientais, sociais e de governança dos principais bancos brasileiros.'
        '</div>'
        '</div>',
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
        default=[],
        label_visibility="collapsed",
        placeholder="Todos os bancos",
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


def render_trend_chart(monthly_counts: list[dict]) -> None:
    """Renderiza um line chart com evolução E/S/G ao longo dos meses."""
    if not monthly_counts:
        st.caption("Sem dados suficientes para o gráfico de tendência.")
        return

    st.markdown("### 📈 Tendência ESG nos últimos meses")
    chart_data = {
        "month": [],
        "Ambiental": [],
        "Social": [],
        "Governança": [],
    }
    for m in monthly_counts:
        try:
            y, mo = m["month"].split("-")
            label = f"{MONTHS_PT[int(mo) - 1][:3]}/{y[2:]}"
        except Exception:
            label = m["month"]
        chart_data["month"].append(label)
        chart_data["Ambiental"].append(m.get("E", 0))
        chart_data["Social"].append(m.get("S", 0))
        chart_data["Governança"].append(m.get("G", 0))

    import pandas as pd
    df = pd.DataFrame(chart_data).set_index("month")
    try:
        st.line_chart(df, color=["#2ecc71", "#3498db", "#9b59b6"], height=260)
    except Exception:
        # Fallback para ambientes sem Altair (ex: Python 3.14 com altair quebrado)
        _render_trend_html(df)


def _render_trend_html(df) -> None:
    """Renderização manual em HTML quando st.line_chart falha."""
    max_val = max(df.values.max(), 1)
    rows_html = []
    colors = {"Ambiental": "#2ecc71", "Social": "#3498db", "Governança": "#9b59b6"}
    for col in df.columns:
        bars = []
        for idx, val in zip(df.index, df[col]):
            pct = int(val / max_val * 100)
            bars.append(
                f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">'
                f'<div style="width:100%;height:80px;display:flex;align-items:flex-end;">'
                f'<div style="width:100%;height:{pct}%;background:{colors[col]};border-radius:3px 3px 0 0;"></div>'
                f'</div>'
                f'<div style="font-size:0.7rem;opacity:0.7;">{idx}</div>'
                f'<div style="font-size:0.75rem;font-weight:700;">{val}</div>'
                f'</div>'
            )
        rows_html.append(
            f'<div style="margin-bottom:16px;">'
            f'<div style="font-weight:600;color:{colors[col]};margin-bottom:6px;">{col}</div>'
            f'<div style="display:flex;gap:8px;align-items:flex-end;">{"".join(bars)}</div>'
            f'</div>'
        )
    st.markdown("".join(rows_html), unsafe_allow_html=True)
