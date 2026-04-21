import streamlit as st
from datetime import date
from calendar import monthrange

from config.settings import BANK_DISPLAY_NAMES, BANK_COLORS, ESG_EMOJIS

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


def render_ranking(bank_counts: dict[str, int], top_n: int = 3) -> None:
    """Podium com os top N bancos mais ativos no período."""
    ranked = sorted(bank_counts.items(), key=lambda x: -x[1])[:top_n]
    ranked = [(b, n) for b, n in ranked if n > 0]
    if not ranked:
        return

    st.markdown("### 🏆 Ranking do período")
    medals = ["🥇", "🥈", "🥉"]
    max_val = ranked[0][1] or 1

    cards = []
    for i, (bank, count) in enumerate(ranked):
        color = BANK_COLORS.get(bank, "#6c757d")
        name = BANK_DISPLAY_NAMES.get(bank, bank)
        medal = medals[i] if i < len(medals) else f"{i + 1}º"
        pct = int(count / max_val * 100)
        cards.append(
            f'<div style="flex:1;background:color-mix(in srgb, {color} 8%, transparent);'
            f'border-left:4px solid {color};border-radius:8px;padding:14px 16px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
            f'<span style="font-size:1.3rem;">{medal}</span>'
            f'<span style="font-size:1.6rem;font-weight:800;color:{color};">{count}</span>'
            f'</div>'
            f'<div style="font-weight:600;margin-bottom:6px;">{name}</div>'
            f'<div style="height:5px;background:color-mix(in srgb, {color} 15%, transparent);border-radius:3px;overflow:hidden;">'
            f'<div style="width:{pct}%;height:100%;background:{color};"></div>'
            f'</div>'
            f'</div>'
        )
    st.markdown(
        f'<div style="display:flex;gap:12px;margin-bottom:16px;">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_trend_chart(monthly_counts: list[dict]) -> None:
    """Renderiza bar chart empilhado com evolução E/S/G ao longo dos meses."""
    if not monthly_counts:
        st.caption("Sem dados suficientes para o gráfico de tendência.")
        return

    st.markdown("### 📈 Tendência ESG nos últimos meses")

    # Ordena cronologicamente pelo mês (formato YYYY-MM garante ordem lexicográfica)
    ordered = sorted(monthly_counts, key=lambda m: m["month"])

    import pandas as pd
    rows = []
    for m in ordered:
        try:
            y, mo = m["month"].split("-")
            label = f"{MONTHS_PT[int(mo) - 1][:3]}/{y[2:]}"
        except Exception:
            label = m["month"]
        rows.append({"mes": label, "Ambiental": m.get("E", 0),
                     "Social": m.get("S", 0), "Governança": m.get("G", 0)})

    df = pd.DataFrame(rows)
    month_order = df["mes"].tolist()  # ordem cronológica já garantida acima

    try:
        import altair as alt
        long = df.melt(id_vars="mes", var_name="Categoria", value_name="Notícias")
        chart = (
            alt.Chart(long)
            .mark_bar()
            .encode(
                x=alt.X("mes:N", title=None, sort=month_order,
                        axis=alt.Axis(labelAngle=0)),
                xOffset=alt.XOffset("Categoria:N"),
                y=alt.Y("Notícias:Q", title=None),
                color=alt.Color(
                    "Categoria:N",
                    scale=alt.Scale(
                        domain=["Ambiental", "Social", "Governança"],
                        range=["#2ecc71", "#3498db", "#9b59b6"],
                    ),
                    legend=alt.Legend(orient="bottom", title=None),
                ),
                tooltip=["mes", "Categoria", "Notícias"],
            )
            .properties(height=300)
        )
        st.altair_chart(chart, use_container_width=True)
    except Exception:
        _render_trend_html(df.set_index("mes"))


def _render_trend_html(df) -> None:
    """Renderização manual quando st.line_chart falha — grouped bar chart."""
    max_val = max(df.values.max(), 1)
    colors = {"Ambiental": "#2ecc71", "Social": "#3498db", "Governança": "#9b59b6"}
    BAR_MAX_HEIGHT = 120  # px

    # Legenda
    legend = " &nbsp;•&nbsp; ".join(
        f'<span style="color:{c};font-weight:600;">● {name}</span>'
        for name, c in colors.items()
    )

    # Grupos por mês, com 3 barras (E/S/G) lado a lado
    groups = []
    for idx in df.index:
        bars = []
        for col in df.columns:
            val = int(df.loc[idx, col])
            h = int(val / max_val * BAR_MAX_HEIGHT) if val > 0 else 2
            bars.append(
                f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px;">'
                f'<div style="font-size:0.7rem;font-weight:700;color:{colors[col]};">{val}</div>'
                f'<div style="width:22px;height:{h}px;background:{colors[col]};border-radius:3px 3px 0 0;"></div>'
                f'</div>'
            )
        groups.append(
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;">'
            f'<div style="display:flex;gap:6px;align-items:flex-end;height:{BAR_MAX_HEIGHT + 20}px;">{"".join(bars)}</div>'
            f'<div style="font-size:0.75rem;opacity:0.75;font-weight:500;">{idx}</div>'
            f'</div>'
        )

    html = (
        f'<div style="margin-bottom:8px;font-size:0.8rem;">{legend}</div>'
        f'<div style="display:flex;gap:16px;align-items:flex-end;padding:8px 0 16px 0;">'
        f'{"".join(groups)}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
