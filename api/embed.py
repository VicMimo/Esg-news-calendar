from config.settings import BANK_COLORS, BANK_COLORS_LIGHT, BANK_DISPLAY_NAMES, ESG_COLORS, ESG_EMOJIS


def build_embed_html(articles: list[dict], title: str = "ESG News Calendar") -> str:
    from collections import defaultdict
    import calendar
    from datetime import date

    today = date.today()

    if articles:
        first_date = date.fromisoformat(str(articles[-1]["data"]))
        year, month = first_date.year, first_date.month
    else:
        year, month = today.year, today.month

    by_date: dict[str, list[dict]] = defaultdict(list)
    for a in articles:
        by_date[str(a["data"])].append(a)

    cal = calendar.monthcalendar(year, month)
    months_pt = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]
    days_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    def card_html(a: dict) -> str:
        banco_tag = a.get("banco_tag", "")
        esg_tag = a.get("esg_tag", "unknown")
        color = BANK_COLORS.get(banco_tag, "#6c757d")
        light = BANK_COLORS_LIGHT.get(banco_tag, "#dee2e6")
        esg_color = ESG_COLORS.get(esg_tag, "#6c757d")
        emoji = ESG_EMOJIS.get(esg_tag, "📰")
        banco = BANK_DISPLAY_NAMES.get(banco_tag, banco_tag)
        titulo = a.get("titulo", "")
        if len(titulo) > 65:
            titulo = titulo[:62] + "..."
        link = a.get("link", "#")
        return (
            f'<div style="border-left:4px solid {color};background:{light};'
            f'border-radius:5px;padding:6px 8px;margin-bottom:5px;font-size:11px;line-height:1.3;">'
            f'<div style="font-size:9px;font-weight:700;text-transform:uppercase;margin-bottom:2px;opacity:.7;">'
            f'{banco} · <span style="background:{esg_color};color:#fff;border-radius:3px;padding:1px 4px;">{emoji} {esg_tag}</span></div>'
            f'<a href="{link}" target="_blank" style="text-decoration:none;color:inherit;font-weight:600;">{titulo}</a>'
            f'</div>'
        )

    header_cells = "".join(
        f'<th style="font-size:11px;color:#6c757d;text-transform:uppercase;padding:6px 4px;'
        f'border-bottom:2px solid #dee2e6;text-align:center;">{d}</th>'
        for d in days_pt
    )

    rows_html = ""
    for week in cal:
        cells = ""
        for day in week:
            if day == 0:
                cells += '<td style="min-height:100px;border-top:1px solid #eee;padding:4px;vertical-align:top;"></td>'
            else:
                d = date(year, month, day)
                is_today = d == today
                num_style = "font-weight:700;font-size:13px;color:#e63946;" if is_today else "font-weight:700;font-size:12px;color:#495057;"
                day_articles = by_date.get(d.isoformat(), [])
                cards = "".join(card_html(a) for a in day_articles)
                cells += (
                    f'<td style="min-height:100px;border-top:1px solid #eee;padding:4px;vertical-align:top;">'
                    f'<div style="{num_style}text-align:right;margin-bottom:4px;">{day}</div>'
                    f'{cards}</td>'
                )
        rows_html += f"<tr>{cells}</tr>"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 16px; background: #f8f9fa; }}
  h2 {{ margin: 0 0 12px; font-size: 18px; color: #212529; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  td, th {{ padding: 4px; }}
  a:hover {{ text-decoration: underline !important; }}
</style>
</head>
<body>
<h2>🌱 {title} — {months_pt[month - 1]} {year}</h2>
<table>
  <thead><tr>{header_cells}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</body>
</html>"""
