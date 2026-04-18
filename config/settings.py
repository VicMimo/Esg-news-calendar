from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "esg_news.db"

BANK_QUERIES = {
    "itau": [
        "Itaú ESG", "Itaú sustentabilidade", "Itaú BBA sustentabilidade",
        "Itaú verde", "Itaú net zero", "Itaú Unibanco ESG",
    ],
    "bradesco": [
        "Bradesco ESG", "Bradesco sustentabilidade", "Bradesco social",
        "Bradesco verde", "Bradesco Next ESG",
    ],
    "santander": [
        "Santander ESG", "Santander títulos verdes",
        "Santander sustentável", "Santander sustentabilidade",
    ],
    "bb": [
        "Banco do Brasil ESG", "BB sustentabilidade",
        "Banco do Brasil verde", "Banco do Brasil ambiental",
    ],
    "caixa": [
        "Caixa ESG", "Caixa sustentabilidade",
        "Caixa habitação social", "Caixa verde",
    ],
    "btg": [
        "BTG ESG", "BTG Pactual sustentabilidade",
        "BTG verde", "BTG Pactual ambiental",
    ],
    "nubank": [
        "Nubank ESG", "Nubank sustentabilidade",
        "Nubank social", "Nubank impacto",
    ],
    "safra": [
        "Banco Safra ESG", "Banco Safra sustentabilidade",
        "Banco Safra verde", "Banco Safra ambiental",
        "Banco Safra social",
    ],
    "xp": [
        "XP Investimentos ESG", "XP sustentabilidade",
        "XP verde", "XP impacto social",
    ],
    "inter": [
        "Banco Inter ESG", "Inter sustentabilidade",
        "Inter social", "Inter verde",
    ],
    "c6": [
        "C6 Bank ESG", "C6 Bank sustentabilidade",
        "C6 Bank social", "C6 Bank verde",
    ],
    "sicoob": [
        "Sicoob ESG", "Sicoob sustentabilidade",
        "Sicoob social", "Sicoob cooperativa verde",
    ],
}

ESG_KEYWORDS = {
    "E": [
        "carbono", "carbon", "emissão", "emissões", "clima", "climate",
        "verde", "green bond", "green bonds", "sustentável", "sustainable",
        "ambiental", "environmental", "energia renovável", "renewable energy",
        "solar", "eólica", "wind", "floresta", "forest", "desmatamento",
        "deforestation", "biodiversidade", "biodiversity", "títulos verdes",
        "crédito verde", "financiamento verde", "pegada", "footprint",
        "reciclagem", "recycling", "água", "water", "aquecimento global",
        "net zero", "neutralidade de carbono", "descarbonização", "ESG ambiental",
        "emissão zero", "zero emissão", "crédito de carbono", "compensação carbono",
    ],
    "S": [
        "social", "inclusão", "inclusion", "diversidade", "diversity",
        "gênero", "gender", "mulher", "women", "racial", "etnia", "ethnicity",
        "comunidade", "community", "habitação", "housing", "moradia",
        "educação", "education", "saúde", "health", "trabalho", "emprego",
        "microcrédito", "microcredit", "inclusão financeira", "financial inclusion",
        "vulnerável", "vulnerable", "pobreza", "poverty", "desigualdade",
        "direitos humanos", "human rights", "trabalhador", "worker",
        "liderança feminina", "conselho diverso", "equidade", "equity",
        "refugiado", "acessibilidade", "accessibility", "comunidades",
    ],
    "G": [
        "governança", "governance", "transparência", "transparency",
        "conselho", "board", "diretoria", "compliance", "ética", "ethics",
        "anticorrupção", "anti-corruption", "regulatório", "regulatory",
        "risco", "risk", "auditoria", "audit", "relatório anual", "annual report",
        "política", "policy", "código de conduta", "code of conduct",
        "remuneração executiva", "executive pay", "acionista", "shareholder",
        "LGPD", "privacidade", "privacy", "dados", "data protection",
        "integridade", "integrity", "ESG relatório", "divulgação", "disclosure",
    ],
}

BANK_DISPLAY_NAMES = {
    "itau":      "Itaú",
    "bradesco":  "Bradesco",
    "santander": "Santander",
    "bb":        "Banco do Brasil",
    "caixa":     "Caixa",
    "btg":       "BTG Pactual",
    "nubank":    "Nubank",
    "safra":     "Safra",
    "xp":        "XP Investimentos",
    "inter":     "Inter",
    "c6":        "C6 Bank",
    "sicoob":    "Sicoob",
}

# Official brand colors (primary color for card border)
BANK_COLORS = {
    "itau":      "#EC7000",
    "bradesco":  "#CC092F",
    "santander": "#EC0000",
    "bb":        "#D4A017",
    "caixa":     "#005CA9",
    "btg":       "#1A1A2E",
    "nubank":    "#820AD1",
    "safra":     "#003B5C",
    "xp":        "#000000",
    "inter":     "#FF7A00",
    "c6":        "#242424",
    "sicoob":    "#007A3D",
}

# Lightened brand colors for card backgrounds
BANK_COLORS_LIGHT = {
    "itau":      "#FDE8D0",
    "bradesco":  "#FAD0D7",
    "santander": "#FAD0D0",
    "bb":        "#FEF5CC",
    "caixa":     "#CCE2F4",
    "btg":       "#D0D0DC",
    "nubank":    "#EDD5FA",
    "safra":     "#CCDAE3",
    "xp":        "#DEDEDE",
    "inter":     "#FFE4CC",
    "c6":        "#D8D8D8",
    "sicoob":    "#CCE8D9",
}

# Iniciais dos bancos para o badge SVG inline (não depende de URL externa)
BANK_INITIALS = {
    "itau":      "IT",
    "bradesco":  "BR",
    "santander": "SA",
    "bb":        "BB",
    "caixa":     "CX",
    "btg":       "BT",
    "nubank":    "NU",
    "safra":     "SF",
    "xp":        "XP",
    "inter":     "IN",
    "c6":        "C6",
    "sicoob":    "SC",
}

# Whitelist fechada — jornais renomados, reguladores, entidades do setor e canais
# oficiais dos bancos. Qualquer domínio fora desta lista é rejeitado.
TRUSTED_DOMAINS = {
    # --- Jornais e revistas financeiras ---
    "valoreconomico.com.br",
    "valor.globo.com",
    "estadao.com.br",
    "einvestidor.estadao.com.br",
    "folha.uol.com.br",
    "estudio.folha.uol.com.br",
    "exame.com",
    "infomoney.com.br",
    "moneytimes.com.br",
    "istoedinheiro.com.br",
    "neofeed.com.br",
    "braziljournal.com",
    "capital.com.br",
    "dci.com.br",
    "seudinheiro.com",
    "suno.com.br",
    # --- Agências de notícias internacionais ---
    "bloomberg.com",
    "bloomberg.com.br",
    "reuters.com",
    "ft.com",
    # --- TV e portais jornalísticos ---
    "cnnbrasil.com.br",
    "g1.globo.com",
    "agenciabrasil.ebc.com.br",
    "band.uol.com.br",
    "jovempan.news",
    # --- Reguladores e órgãos governamentais ---
    "bcb.gov.br",
    "cvm.gov.br",
    "fazenda.gov.br",
    "mma.gov.br",
    "planalto.gov.br",
    "senado.leg.br",
    "agencia.senado.leg.br",
    "camara.leg.br",
    # --- Entidades do setor financeiro e ESG ---
    "febraban.org.br",
    "b3.com.br",
    "anbima.com.br",
    "abrapp.org.br",
    "abbc.org.br",
    "amecbrasil.org.br",
    "gri-standards.org",
    "cdp.net",
    "unpri.org",
    "sbfin.org.br",
    "terraotb.org.br",
    # --- Canais oficiais dos bancos e subsidiárias ---
    "itau.com.br",
    "ri.itau.com.br",
    "itaubba.com",
    "bradesco.com.br",
    "ri.bradesco.com.br",
    "next.me",
    "santander.com.br",
    "bb.com.br",
    "agencia.bb.com.br",
    "caixa.gov.br",
    "btgpactual.com",
    "nubank.com.br",
    "international.nubank.com.br",
    "safra.com.br",
    "oespecialista.safra.com.br",
    "xpi.com.br",
    "conteudos.xpi.com.br",
    "bancointer.com.br",
    "c6bank.com.br",
    "sicoob.com.br",
}

ESG_LABELS = {
    "E": "Ambiental",
    "S": "Social",
    "G": "Governança",
    "unknown": "Não classificado",
}

ESG_COLORS = {
    "E": "#2d6a4f",
    "S": "#1d3557",
    "G": "#6a0572",
    "unknown": "#6c757d",
}

ESG_COLORS_LIGHT = {
    "E": "#b7e4c7",
    "S": "#a8dadc",
    "G": "#e2b0ff",
    "unknown": "#dee2e6",
}

ESG_EMOJIS = {
    "E": "🌱",
    "S": "🤝",
    "G": "⚖️",
    "unknown": "📰",
}
