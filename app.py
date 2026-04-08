import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import numpy as np
import base64

# ──────────────────────────────────────────────
# 1. CONFIG
# ──────────────────────────────────────────────

st.set_page_config(page_title="TERMINAL", page_icon="favicon.png", layout="wide")

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

icone_base64 = get_base64_of_bin_file("favicon.png")
if icone_base64:
    components.html(
        f"""<script>
const doc = window.parent.document;
let appleIcon = doc.querySelector("link[rel='apple-touch-icon']");
if (!appleIcon)  appleIcon = doc.createElement('link'); appleIcon.rel = 'apple-touch-icon'; doc.head.appendChild(appleIcon); 
appleIcon.href = 'data:image/png;base64,{icone_base64}';
let appleCapable = doc.querySelector("meta[name='apple-mobile-web-app-capable']");
if (!appleCapable)  appleCapable = doc.createElement('meta'); appleCapable.name = 'apple-mobile-web-app-capable'; appleCapable.content = 'yes'; doc.head.appendChild(appleCapable); 
</script>""",
        height=0, width=0
    )

for k, v in [("ticker_selecionado", None), ("periodo_grafico", "12M")]:
    if k not in st.session_state:
        st.session_state[k] = v

hora_atual = datetime.now().strftime("%H:%M")

# ──────────────────────────────────────────────
# 2. CSS – BLOOMBERG TERMINAL
# ──────────────────────────────────────────────

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;700&display=swap');

/* ── BASE ── */
.stApp { background-color: #0a0a0a; font-family: 'IBM Plex Sans', sans-serif; }
*, *::before, *::after { box-sizing: border-box; }
[data-testid="stStatusWidget"] { visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 0.75rem 1rem 2rem !important; max-width: 100% !important; }

/* Sidebar escura */
section[data-testid="stSidebar"] {
    background-color: #0d0d0d !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] {
    gap: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
    gap: 0 !important;
}
/* Esconde as bolas do radio */
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}
/* Estilo de cada item do menu */
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
    border-left: 3px solid transparent !important;
    padding: 8px 8px !important;
    margin: 0 !important;
    cursor: pointer !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p {
    color: #999 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}
/* Item ativo - borda lateral */
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    border-left: 3px solid transparent !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
    color: #FF9900 !important;
    font-weight: 700 !important;
    border-bottom: 1px solid #FF9900 !important;
    padding-bottom: 2px !important;
    display: inline !important;
}
div[data-testid="stDecoration"] { display: none; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }

/* ── HEADER ── */
.terminal-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 0 0 8px 0;
    border-bottom: 1px solid #FF9900;
    margin-bottom: 0;
}
.terminal-brand {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.terminal-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: #FF9900;
    letter-spacing: 4px;
    line-height: 1;
}
.terminal-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: #888;
    letter-spacing: 3px;
}
.terminal-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 2px;
}
.terminal-time {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #aaa;
    letter-spacing: 2px;
}

/* ── NAV BAR ── */
.nav-bar {
    display: flex;
    gap: 0;
    border-bottom: 1px solid #1e1e1e;
    margin: 0 0 12px 0;
    overflow-x: auto;
    scrollbar-width: none;
}
.nav-bar::-webkit-scrollbar { display: none; }

/* ── SELECTBOX (NAV) ── */
div[data-testid="stSelectbox"] label {
    color: #aaa !important;
    font-size: 0.65rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-family: 'IBM Plex Mono', monospace !important;
    margin-bottom: 6px !important;
}
div[data-testid="stSelectbox"] svg { color: #777 !important; }
div[data-testid="stSelectbox"] ul {
    background-color: #111 !important;
    border: 1px solid #222 !important;
}
div[data-testid="stSelectbox"] li {
    font-size: 0.75rem !important;
    color: #ccc !important;
}
div[data-testid="stSelectbox"] li:hover { background-color: #1a1a1a !important; }

/* ── DIVIDER ── */
hr { border: none; border-top: 1px solid #1a1a1a !important; margin: 6px 0 !important; }

/* ── PILLS ── */
[data-testid="stBaseButton-pills"] {
    background-color: transparent !important;
    border: none !important;
    color: #999 !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 1px !important;
    padding: 4px 10px !important;
    text-transform: uppercase !important;
}
[data-testid="stBaseButton-pillsActive"] {
    background-color: transparent !important;
    color: #FF9900 !important;
    border: none !important;
    border-bottom: 1px solid #FF9900 !important;
    border-radius: 0 !important;
    font-weight: 700 !important;
}

/* ── BUTTONS ── */
div.stButton > button {
    background-color: transparent !important;
    color: #FF9900 !important;
    border: 1px solid #333 !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 2px !important;
    padding: 4px 12px !important;
    transition: border-color 0.1s;
}
div.stButton > button:hover { border-color: #FF9900 !important; }
div[data-testid="stPopover"] > button {
    height: auto !important;
    min-height: 0 !important;
    padding: 4px 12px !important;
    background-color: transparent !important;
    color: #FF9900 !important;
    border: 1px solid #333 !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 1px !important;
}
div[data-testid="stPopoverBody"] { background-color: #0d0d0d !important; border: 1px solid #2a2a2a !important; border-radius: 0 !important; }

/* ── INPUTS ── */
div[data-testid="stTextInput"] input,
div[data-testid="stDateInput"] input {
    background-color: #0d0d0d !important;
    border: 1px solid #222 !important;
    border-radius: 0 !important;
    color: #e0e0e0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stSelectbox"] label { color: #aaa !important; font-size: 0.65rem !important; letter-spacing: 1px !important; text-transform: uppercase !important; font-family: 'IBM Plex Mono', monospace !important; margin-bottom: 6px !important; display: block !important; }

/* ── DATA EDITOR ── */
div[data-testid="stDataEditor"] { border: 1px solid #1e1e1e !important; border-radius: 0 !important; }

/* ── DOWNLOAD BUTTON ── */
div[data-testid="stDownloadButton"] > button { background: transparent !important; border: 1px solid #333 !important; border-radius: 0 !important; color: #FF9900 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.65rem !important; letter-spacing: 1px !important; padding: 4px 12px !important; }

/* ── ALERTS ── */
div[data-testid="stAlert"] { border-radius: 0 !important; border-left: 2px solid #FF9900 !important; background: #0d0d0d !important; font-size: 0.75rem !important; }

/* ── VALUE COLORS ── */
.pos { color: #00C853 !important; }
.neg { color: #FF3D3D !important; }
.neu { color: #e0e0e0 !important; }
.amber { color: #FF9900 !important; }

/* ── MAIN TABLE ── */
.bb-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    border: 1px solid #1a1a1a;
    margin-top: 8px;
}
.bb-table thead tr { background: #0d0d0d; border-bottom: 1px solid #FF9900; }
.bb-table thead th {
    padding: 6px 8px;
    color: #FF9900;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.6rem;
    border-right: 1px solid #1a1a1a;
    white-space: nowrap;
    text-align: right;
}
.bb-table thead th:first-child { text-align: left; }
.bb-table tbody tr { border-bottom: 1px solid #111; transition: background 0.1s; }
.bb-table tbody tr:hover { background: #0f0f0f; }
.bb-table tbody td {
    padding: 5px 8px;
    color: #d0d0d0;
    border-right: 1px solid #111;
    text-align: right;
    white-space: nowrap;
    font-size: 0.72rem;
}
.bb-table tbody td:first-child { text-align: left; color: #e8e8e8; font-weight: 500; }
.bb-table .sector-row { background: #0d0d0d; }
.bb-table .sector-row td { color: #FF9900; font-weight: 700; letter-spacing: 2px; font-size: 0.62rem; text-align: left; padding: 7px 8px; border-top: 1px solid #1e1e1e; }
.ticker-sym { color: #fff; font-weight: 700; letter-spacing: 0.5px; }
.rec-compra { color: #00C853; font-size: 0.65rem; font-weight: 700; }
.rec-neutro { color: #888; font-size: 0.65rem; }
.rec-venda { color: #FF3D3D; font-size: 0.65rem; font-weight: 700; }

/* ── RENTABILIDADE TABLE ── */
.rent-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    border: 1px solid #1a1a1a;
    margin-top: 12px;
}
.rent-table th { background: #0d0d0d; color: #FF9900; padding: 6px 4px; border: 1px solid #1a1a1a; text-transform: uppercase; font-size: 0.58rem; letter-spacing: 1px; text-align: center; }
.rent-table td { padding: 5px 4px; border: 1px solid #111; color: #e0e0e0; text-align: center; font-variant-numeric: tabular-nums; }
.rent-year { background: #0d0d0d !important; font-weight: 700; color: #e0e0e0 !important; text-align: left !important; padding-left: 8px !important; }
.rent-total { background: #0d0d0d; font-weight: 700; }

/* ── SECTION LABEL ── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin: 24px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1a1a1a;
}
.chart-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #bbb;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 6px;
}

/* ── MOBILE ACCORDION ── */
details {
    background: #0a0a0a;
    border-bottom: 1px solid #111;
    margin-bottom: 0;
    font-family: 'IBM Plex Mono', monospace;
}
summary {
    list-style: none;
    padding: 8px 10px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #0a0a0a;
}
summary:hover { background: #0f0f0f; }
.mob-header-left { display: flex; align-items: center; gap: 8px; }
.mob-header-right { display: flex; flex-direction: column; align-items: flex-end; gap: 1px; }
.mob-ticker { font-weight: 700; color: #fff; font-size: 0.78rem; letter-spacing: 0.5px; }
.mob-price { color: #aaa; font-size: 0.7rem; font-weight: 500; }
.mob-today { font-weight: 700; font-size: 0.72rem; }
.mob-content { padding: 8px 10px; background: #0d0d0d; border-top: 1px solid #111; }
.mob-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
.mob-item { display: flex; flex-direction: column; gap: 1px; }
.mob-label { color: #aaa; font-size: 0.55rem; text-transform: uppercase; letter-spacing: 1px; }
.mob-val { color: #e0e0e0; font-size: 0.72rem; font-weight: 500; }
.mob-sector { background: #0d0d0d; color: #FF9900; padding: 7px 10px; font-weight: 700; font-size: 0.65rem; letter-spacing: 2px; border-bottom: 1px solid #1e1e1e; margin-top: 10px; }

/* ── RESPONSIVE ── */
.desktop-view { display: block; }
.mobile-view { display: none; }

/* Wrapper para tabelas com scroll horizontal no mobile */
.table-scroll-wrapper {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}


@media (max-width: 768px) {
    html, body, .stApp {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    .block-container {
        padding: 0.4rem 0.6rem 2rem !important;
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }

    .terminal-title { font-size: 1rem; letter-spacing: 2px; }
    .terminal-sub { font-size: 0.5rem; letter-spacing: 2px; }
    .terminal-time { font-size: 0.55rem; }
    
    /* SYNC button – espaçamento do header */
    div.stButton { margin-top: 6px !important; }

    .desktop-view { display: none !important; }
    .mobile-view { display: block !important; }

    /* Tabelas com scroll horizontal interno */
    .bb-table, .rent-table {
        display: block;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        max-width: 100vw;
        touch-action: pan-x pan-y;
    }

    div[data-testid="stPopover"] { display: none !important; }

    details {
        border: none !important;
        border-bottom: 1px solid #111 !important;
        border-radius: 0 !important;
        margin-bottom: 0 !important;
    }
    summary { padding: 10px 8px !important; }
    .mob-ticker { font-size: 0.75rem; }
    .mob-price { font-size: 0.68rem; }
    .mob-today { font-size: 0.7rem; }
    .mob-content { padding: 8px; }
    .mob-grid { gap: 8px; }
    .mob-label { font-size: 0.5rem; letter-spacing: 1.5px; }
    .mob-val { font-size: 0.68rem; }
    .mob-sector {
        margin: 14px 0 4px !important;
        padding: 8px 8px !important;
        font-size: 0.6rem !important;
        letter-spacing: 2px !important;
        border-bottom: 1px solid #FF9900 !important;
        background: transparent !important;
    }

    .section-label {
        font-size: 0.55rem !important;
        margin: 18px 0 8px 0 !important;
        letter-spacing: 2px !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stDateInput"] input {
        font-size: 0.7rem !important;
        padding: 6px 8px !important;
    }

    .js-plotly-plot, .plotly {
        max-width: 100% !important;
        overflow: hidden !important;
    }
}
</style>

""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 3. DICIONÁRIOS
# ──────────────────────────────────────────────

APORTES_USUARIO = [
    {"ticker": "WEGE3.SA", "data": "2025-08-26", "qtd": 3},
    {"ticker": "EQTL3.SA", "data": "2025-08-26", "qtd": 2},
    {"ticker": "MULT3.SA", "data": "2025-08-26", "qtd": 2},
    {"ticker": "RENT3.SA", "data": "2025-08-26", "qtd": 1},
    {"ticker": "LEVE3.SA", "data": "2025-08-26", "qtd": 1},
    {"ticker": "ITUB3.SA", "data": "2025-09-16", "qtd": 8},
    {"ticker": "EQTL3.SA", "data": "2025-09-16", "qtd": 2},
    {"ticker": "EGIE3.SA", "data": "2025-09-16", "qtd": 3},
    {"ticker": "MULT3.SA", "data": "2025-09-16", "qtd": 2},
    {"ticker": "RADL3.SA", "data": "2025-09-16", "qtd": 5},
    {"ticker": "SMFT3.SA", "data": "2025-09-16", "qtd": 1},
    {"ticker": "MDIA3.SA", "data": "2025-09-16", "qtd": 1},
    {"ticker": "BBSE3.SA", "data": "2025-09-16", "qtd": 3},
    {"ticker": "LREN3.SA", "data": "2025-09-16", "qtd": 3},
    {"ticker": "BPAC3.SA", "data": "2025-09-16", "qtd": 2},
    {"ticker": "VIVT3.SA", "data": "2025-09-16", "qtd": 3},
    {"ticker": "ASAI3.SA", "data": "2025-09-16", "qtd": 4},
    {"ticker": "UNIP3.SA", "data": "2025-09-16", "qtd": 1},
    {"ticker": "PSSA3.SA", "data": "2025-09-16", "qtd": 2},
    {"ticker": "PRIO3.SA", "data": "2025-09-16", "qtd": 1},
    {"ticker": "WEGE3.SA", "data": "2025-11-14", "qtd": 2},
    {"ticker": "MULT3.SA", "data": "2025-11-14", "qtd": 3},
    {"ticker": "LEVE3.SA", "data": "2025-11-14", "qtd": 4},
    {"ticker": "UNIP3.SA", "data": "2025-11-14", "qtd": 1},
    {"ticker": "PSSA3.SA", "data": "2025-11-14", "qtd": 3},
    {"ticker": "EGIE3.SA", "data": "2025-11-28", "qtd": 1},
    {"ticker": "EGIE3.SA", "data": "2025-12-05", "qtd": 5},
    {"ticker": "EQTL3.SA", "data": "2025-12-05", "qtd": 1},
    {"ticker": "RENT3.SA", "data": "2025-12-05", "qtd": 2},
    {"ticker": "VULC3.SA", "data": "2025-12-05", "qtd": 5},
    {"ticker": "EQTL3.SA", "data": "2025-12-19", "qtd": 4},
    {"ticker": "SMFT3.SA", "data": "2025-12-19", "qtd": 5},
    {"ticker": "MDIA3.SA", "data": "2025-12-19", "qtd": 4},
    {"ticker": "ASAI3.SA", "data": "2025-12-19", "qtd": 10},
    {"ticker": "PRIO3.SA", "data": "2025-12-19", "qtd": 4},
    {"ticker": "VALE3.SA", "data": "2026-01-23", "qtd": 3},
    {"ticker": "MDIA3.SA", "data": "2026-02-09", "qtd": -5},
    {"ticker": "SBSP3.SA", "data": "2026-02-09", "qtd": 1},
]

INDICES_LIST = ["^BVSP", "SMALL11.SA", "EWZ", "^GSPC", "^NDX", "^DJI", "^VIX", "^N225",
                "^HSI", "000001.SS", "^GDAXI", "^FTSE", "^FCHI", "^STOXX50E",
                "BRL=X", "DX-Y.NYB", "BTC-USD", "ES=F", "BZ=F", "TIO=F", "GC=F"]

COBERTURA = {
    "AZZA3.SA": {"Rec": "Compra", "Alvo": 50.00}, "LREN3.SA": {"Rec": "Compra", "Alvo": 23.00},
    "MGLU3.SA": {"Rec": "Neutro", "Alvo": 10.00}, "MELI":     {"Rec": "Compra", "Alvo": 2810.00},
    "ASAI3.SA": {"Rec": "Compra", "Alvo": 18.00}, "RADL3.SA": {"Rec": "Compra", "Alvo": 29.00},
    "SMFT3.SA": {"Rec": "Compra", "Alvo": 36.00}, "NATU3.SA": {"Rec": "Compra", "Alvo": 15.00},
    "AUAU3.SA": {"Rec": "Neutro", "Alvo": 3.00},  "ABEV3.SA": {"Rec": "Neutro", "Alvo": 15.00},
    "MULT3.SA": {"Rec": "Compra", "Alvo": 35.00}, "WEGE3.SA": {"Rec": "Neutro", "Alvo": 49.00},
    "RENT3.SA": {"Rec": "Compra", "Alvo": 58.00}, "SLCE3.SA": {"Rec": "Compra", "Alvo": 24.60},
    "JBS":      {"Rec": "Compra", "Alvo": 20.00}, "MBRF3.SA": {"Rec": "Neutro", "Alvo": 22.00},
    "BEEF3.SA": {"Rec": "Neutro", "Alvo": 7.00},  "EZTC3.SA": {"Rec": "Compra", "Alvo": 24.00},
    "MRVE3.SA": {"Rec": "Neutro", "Alvo": 9.50},
}

SETORES_ACOMPANHAMENTO = {
    "IBOV":                        ["^BVSP"],
    "Varejo e Bens de Consumo":    ["AZZA3.SA","LREN3.SA","CEAB3.SA","RIAA3.SA","TFCO4.SA","VIVA3.SA","SBFG3.SA","MELI","MGLU3.SA","BHIA3.SA","ASAI3.SA","GMAT3.SA","PCAR3.SA","SMFT3.SA","NATU3.SA","AUAU3.SA","VULC3.SA","ALPA4.SA"],
    "Farmácias e Farmacêuticas":   ["RADL3.SA","PGMN3.SA","PNVL3.SA","DMVF3.SA","PFRM3.SA","HYPE3.SA","BLAU3.SA"],
    "Shoppings":                   ["MULT3.SA","ALOS3.SA","IGTI11.SA"],
    "Agronegócio e Proteínas":     ["AGRO3.SA","SLCE3.SA","ABEV3.SA","MDIA3.SA","JBS","MBRF3.SA","BEEF3.SA","SMTO3.SA","KEPL3.SA"],
    "Bens de Capital":             ["WEGE3.SA","EMBJ3.SA","LEVE3.SA","TUPY3.SA","MYPK3.SA","FRAS3.SA","RAPT4.SA","POMO4.SA"],
    "Transporte e Logística":      ["RENT3.SA","MOVI3.SA","VAMO3.SA","RAIL3.SA","SIMH3.SA"],
    "Bancos e Financeiras":        ["ITUB4.SA","BBDC4.SA","BBAS3.SA","SANB11.SA","NU","BPAC11.SA","XP","INTR","PAGS","BRSR6.SA","B3SA3.SA","BBSE3.SA","PSSA3.SA","CXSE3.SA"],
    "Educação":                    ["YDUQ3.SA","COGN3.SA","ANIM3.SA","SEER3.SA"],
    "Energia Elétrica":            ["AXIA3.SA","AURE3.SA","EQTL3.SA","EGIE3.SA","TAEE11.SA","ENEV3.SA","CMIG4.SA","CPLE3.SA","CPFE3.SA","ENGI11.SA","ISA4.SA","ALUP11.SA"],
    "Água e Saneamento":           ["SBSP3.SA","SAPR11.SA","CSMG3.SA","ORVR3.SA"],
    "Concessões":                  ["MOTV3.SA","ECOR3.SA"],
    "Saúde":                       ["RDOR3.SA","HAPV3.SA","ODPV3.SA","MATD3.SA","FLRY3.SA"],
    "Tech e Telecom":              ["VIVT3.SA","TIMS3.SA","TOTS3.SA","LWSA3.SA"],
    "Construção e Real Estate":    ["EZTC3.SA","CYRE3.SA","MRVE3.SA","MDNE3.SA","TEND3.SA","MTRE3.SA","PLPL3.SA","DIRR3.SA","CURY3.SA","JHSF3.SA"],
    "Serviços":                    ["OPCT3.SA","GGPS3.SA"],
    "Petróleo, Gás e Distribuição":["PETR4.SA","PRIO3.SA","BRAV3.SA","RECV3.SA","CSAN3.SA","VBBR3.SA","UGPA3.SA"],
    "Mineração e Siderurgia":      ["VALE3.SA","CSNA3.SA","USIM5.SA","GGBR4.SA","GOAU4.SA","CMIN3.SA","BRAP4.SA"],
    "Papel, Celulose e Químicos":  ["SUZB3.SA","KLBN11.SA","RANI3.SA","UNIP6.SA","DEXP3.SA"],
}

DB_MACRO = {
    "Índice de confiança de serviços":               {"fonte": "bcb",  "codigo": 17660,                "freq": "mensal"},
    "CDI anualizado":                                {"fonte": "bcb",  "codigo": 4389,                 "freq": "diario"},
    "TJLP mensal":                                   {"fonte": "bcb",  "codigo": 256,                  "freq": "mensal"},
    "Taxa Selic":                                    {"fonte": "bcb",  "codigo": 432,                  "freq": "diario"},
    "PIB mensal - R$ MM":                            {"fonte": "bcb",  "codigo": 4380,                 "freq": "mensal"},
    "PIB acum. Ano - R$ MM":                         {"fonte": "bcb",  "codigo": 4381,                 "freq": "mensal"},
    "PIB acum. 12m - R$ MM":                         {"fonte": "bcb",  "codigo": 4382,                 "freq": "mensal"},
    "PIB anual - R$ MM":                             {"fonte": "bcb",  "codigo": 1208,                 "freq": "anual"},
    "Meta inflação":                                 {"fonte": "bcb",  "codigo": 13521,                "freq": "anual"},
    "IGP-M - Mensal":                                {"fonte": "bcb",  "codigo": 189,                  "freq": "mensal"},
    "IGP-DI - Mensal":                               {"fonte": "bcb",  "codigo": 190,                  "freq": "mensal"},
    "IPCA - Mensal":                                 {"fonte": "bcb",  "codigo": 433,                  "freq": "mensal"},
    "IPCA alimentos e bebidas - Mensal":             {"fonte": "bcb",  "codigo": 1635,                 "freq": "mensal"},
    "IPCA vestuário - Mensal":                       {"fonte": "bcb",  "codigo": 1638,                 "freq": "mensal"},
    "IPCA geral acum. 12m":                          {"fonte": "bcb",  "codigo": 13522,                "freq": "mensal"},
    "Intenção de consumo das famílias ajustado":     {"fonte": "ipea", "codigo": "CNC12_ICFAJ12",      "freq": "mensal"},
    "Famílias endividadas total":                    {"fonte": "ipea", "codigo": "CNC12_PEICT12",      "freq": "mensal"},
    "Taxa de desemprego":                            {"fonte": "ipea", "codigo": "PNADC12_TDESOC12",   "freq": "mensal"},
    "Massa salarial real":                           {"fonte": "ipea", "codigo": "PNADC12_MRRTH12",    "freq": "mensal"},
    "Renda real habitual":                           {"fonte": "ipea", "codigo": "PNADC12_RRTH12",     "freq": "mensal"},
    "Produção industrial - Bebidas":                 {"fonte": "ipea", "codigo": "PIMPFN12_QIIGNN212", "freq": "mensal"},
    "Volume de vendas no varejo - Geral":            {"fonte": "ipea", "codigo": "PMC12_IVVRN12",      "freq": "mensal"},
    "Volume de vendas - Artigos farmacêuticos":      {"fonte": "ipea", "codigo": "PMC12_VRFARMN12",    "freq": "mensal"},
    "Volume de vendas - Hipermercados":              {"fonte": "ipea", "codigo": "PMC12_VRSUPTN12",    "freq": "mensal"},
    "Volume de vendas - Vestuário e calçados":       {"fonte": "ipea", "codigo": "PMC12_VRVESTN12",    "freq": "mensal"},
    "População no Brasil (projeção)":                {"fonte": "ipea", "codigo": "DEPIS_POPP",         "freq": "anual"},
    "Salário mínimo vigente":                        {"fonte": "ipea", "codigo": "MTE12_SALMIN12",     "freq": "mensal"},
    "Salário mínimo real":                           {"fonte": "ipea", "codigo": "GAC12_SALMINRE12",   "freq": "mensal"},
    "Concessões de crédito PF":                      {"fonte": "ipea", "codigo": "BM12_CCAPF12",       "freq": "mensal"},
    "Concessões de crédito PJ":                      {"fonte": "ipea", "codigo": "BM12_CCAPJ12",       "freq": "mensal"},
    "Taxa média de juros PF":                        {"fonte": "ipea", "codigo": "BM12_CTJPF12",       "freq": "mensal"},
    "Saldo de crédito PF recursos livres":           {"fonte": "ipea", "codigo": "BM12_CRLSPF12",      "freq": "mensal"},
}

# ──────────────────────────────────────────────
# 4. FUNÇÕES
# ──────────────────────────────────────────────

@st.cache_data(ttl=1800)
def get_all_data(tickers):
    try:
        with st.spinner(""):
            data = yf.download(tickers, period="5y", group_by='ticker',
                               auto_adjust=True, progress=False, threads=True)
            return data if not data.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_macro_data(item_name, item_info, start_date=None, end_date=None):
    df_final = pd.DataFrame()
    try:
        if item_info["fonte"] == "bcb":
            code = item_info["codigo"]
            url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json"
            if start_date:
                url += f"&dataInicial={start_date.strftime('%d/%m/%Y')}"
            if end_date:
                url += f"&dataFinal={end_date.strftime('%d/%m/%Y')}"
            df = pd.read_json(url)
            if 'valor' in df.columns:
                df['valor'] = pd.to_numeric(df['valor'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
                df = df.dropna(subset=['valor'])
                df['data'] = pd.to_datetime(df['data'], dayfirst=True)

        elif item_info["fonte"] == "ipea":
            code = item_info["codigo"]
            url = f"https://www.ipeadata.gov.br/api/odata4/Metadados('{code}')/Valores"
            df_raw = pd.read_json(url)
            if 'value' in df_raw.columns:
                df = pd.DataFrame(df_raw['value'].tolist())
                if 'VALDATA' in df.columns and 'VALVALOR' in df.columns:
                    df = df.rename(columns={'VALDATA': 'data', 'VALVALOR': 'valor'})
                    df['data'] = pd.to_datetime(df['data'], errors='coerce', utc=True)
                    df = df.dropna(subset=['data'])
                    df['data'] = df['data'].dt.tz_localize(None)
                else:
                    return pd.DataFrame()
            else:
                return pd.DataFrame()

        if not df.empty:
            if start_date:
                df = df[df['data'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['data'] <= pd.to_datetime(end_date)]
            freq = item_info.get("freq", "diario")
            meses_map = {1:'jan',2:'fev',3:'mar',4:'abr',5:'mai',6:'jun',7:'jul',8:'ago',9:'set',10:'out',11:'nov',12:'dez'}
            if freq == "mensal":
                df['Data'] = df['data'].apply(lambda x: f"{meses_map[x.month]}/{str(x.year)[2:]}")
            elif freq == "anual":
                df['Data'] = df['data'].dt.year.astype(str)
            else:
                df['Data'] = df['data'].dt.strftime('%d/%m/%Y')
            df_final = df[['Data', 'valor']].rename(columns={'valor': 'Valor'})

    except Exception as e:
        st.error(f"Erro ao buscar {item_name}: {e}")
    return df_final

def calc_variation(cl, days=None, ytd=False):
    if cl.empty: return 0.0
    try:
        curr = float(cl.iloc[-1])
        if ytd:
            start_row = cl.loc[f"{datetime.now().year}-01-01":]
            start = float(start_row.iloc[0]) if not start_row.empty else float(cl.iloc[0])
        else:
            idx = -days if len(cl) >= days else 0
            if days == 1 and len(cl) > 1:
                idx = -2
            start = float(cl.iloc[idx])
        return ((curr / start) - 1) * 100
    except Exception:
        return 0.0

def fmt_num(val, decimals=2):
    if pd.isna(val): return "-"
    f = f"{val:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f

def fmt_pct(val):
    if pd.isna(val) or val == 0: return '<span class="neu">-</span>'
    cls = "pos" if val > 0 else "neg"
    sign = "+" if val > 0 else ""
    return f'<span class="{cls}">{sign}{fmt_num(val)}%</span>'

def fmt_price(val, sym=""):
    if pd.isna(val) or val == 0: return "-"
    return f'{sym}{fmt_num(val)}'

def rec_class(rec):
    m = {"Compra": "rec-compra", "Neutro": "rec-neutro", "Venda": "rec-venda"}
    return m.get(rec, "neu")

# ──────────────────────────────────────────────
# 5. CHART HELPERS
# ──────────────────────────────────────────────

CHART_LAYOUT = dict(
    template="plotly_dark",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='IBM Plex Mono, monospace', color='#bbb', size=10),
    margin=dict(l=0, r=0, t=44, b=10),
    dragmode=False,
    xaxis=dict(showgrid=False, fixedrange=True, color='#777', linecolor='#1e1e1e'),
    yaxis=dict(showgrid=True, gridcolor='#1a1a1a', fixedrange=True, color='#777',
               side="right", linecolor='#1e1e1e', tickfont=dict(size=9)),
)

def apply_chart_layout(fig, title="", height=350, legend=False):
    layout = dict(**CHART_LAYOUT)
    layout['height'] = height
    mt = 44
    mb = 10
    if title:
        mt = max(mt, 48)
        layout['title'] = dict(text=title.upper(), font=dict(color='#aaa', size=9, family='IBM Plex Mono'), y=0.98, x=0)
    if legend:
        mt = max(mt, 56)
        layout['legend'] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                                font=dict(size=9, color='#bbb'), bgcolor='rgba(0,0,0,0)')
    layout['margin'] = dict(l=0, r=0, t=mt, b=mb)
    fig.update_layout(**layout)

# ──────────────────────────────────────────────
# 6. POPUP GRÁFICO
# ──────────────────────────────────────────────

@st.dialog("COTAÇÃO", width="large")
def exibir_grafico_popup(t_sel, data):
    per_map = {"30D": 21, "6M": 126, "12M": 252, "5A": 1260, "YTD": "ytd"}
    nova = st.pills("", options=list(per_map.keys()), key="pills_popup",
                     default=st.session_state.periodo_grafico)
    if nova:
        st.session_state.periodo_grafico = nova
    try:
        h_raw = data[t_sel]['Close'].dropna()
    except Exception:
        st.error("Dados insuficientes.")
        return

    p_sel = st.session_state.periodo_grafico
    days = per_map.get(p_sel, 252)
    if days == "ytd":
        df_plot = h_raw.loc[f"{datetime.now().year}-01-01":]
    else:
        df_plot = h_raw.iloc[-days:] if len(h_raw) >= days else h_raw

    if not df_plot.empty:
        perf = ((df_plot.iloc[-1] / df_plot.iloc[0]) - 1) * 100
        color = "#00C853" if perf >= 0 else "#FF3D3D"
        fill_rgb = "0,200,83" if perf >= 0 else "255,61,61"
        y_min, y_max = df_plot.min(), df_plot.max()
        padding = (y_max - y_min) * 0.06 if y_max != y_min else y_min * 0.05

        sign = "+" if perf >= 0 else ""
        st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.8rem; color:#bbb; margin-bottom:4px;">'
                    f'<span style="color:#fff; font-weight:700;">{t_sel}</span>'
                    f'&nbsp;&nbsp;<span style="color:{color}; font-weight:700;">{sign}{perf:.2f}%</span></div>',
                    unsafe_allow_html=True)

        fig = go.Figure(go.Scatter(
            x=df_plot.index, y=df_plot.values,
            line=dict(color=color, width=1.5),
            fill='tozeroy',
            fillcolor=f"rgba({fill_rgb}, 0.05)"
        ))
        popup_layout = dict(**CHART_LAYOUT)
        popup_layout['height'] = 380
        popup_layout['margin'] = dict(l=0, r=0, t=4, b=10)
        popup_layout['yaxis'] = dict(showgrid=True, gridcolor='#1a1a1a', fixedrange=True, side="right",
                                     range=[y_min - padding, y_max + padding], tickfont=dict(size=9), color='#777')
        fig.update_layout(**popup_layout)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ──────────────────────────────────────────────
# 7. HEADER
# ──────────────────────────────────────────────

c_title, c_btn = st.columns([0.9, 0.1])
with c_title:
    st.markdown(
        f'<div class="terminal-header">'
        f'  <div class="terminal-brand">'
        f'    <div class="terminal-title">TERMINAL</div>'
        f'    <div class="terminal-sub">MARKET INTELLIGENCE</div>'
        f'  </div>'
        f'  <div class="terminal-meta">'
        f'    <div class="terminal-time">ATUALIZADO {hora_atual}</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True
    )
with c_btn:
    if st.button("↺ SYNC"):
        st.cache_data.clear()
        st.rerun()

# ──────────────────────────────────────────────
# 8. DADOS MASTER
# ──────────────────────────────────────────────

tickers_carteira_usuario = list(set([item['ticker'] for item in APORTES_USUARIO]))
all_tickers_master = sorted(list(set(
    list(COBERTURA.keys()) +
    [t for s in SETORES_ACOMPANHAMENTO.values() for t in s] +
    tickers_carteira_usuario + INDICES_LIST
)))
master_data = get_all_data(all_tickers_master)

if master_data.empty:
    st.error("DADOS INDISPONÍVEIS. Verifique a conexão e tente novamente.")
    st.stop()

# ──────────────────────────────────────────────
# 9. NAVEGAÇÃO
# ──────────────────────────────────────────────

opcoes_nav = ["Cobertura", "Acompanhamentos", "Carteira pessoal", "Índices",
              "Backtest", "Backtest portfólio", "Banco de dados", "Calendário econômico"]

with st.sidebar:
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace; color:#FF9900; font-size:0.75rem; font-weight:700; letter-spacing:3px; padding:12px 0 10px 0; border-bottom:1px solid #FF9900; margin-bottom:12px;">MENU</div>', unsafe_allow_html=True)
    aba_selecionada = st.radio("", options=opcoes_nav, index=0, key="aba_nav", label_visibility="collapsed")

# ──────────────────────────────────────────────
# 10. ABA: BANCO DE DADOS
# ──────────────────────────────────────────────

if aba_selecionada == "Banco de dados":
    c_sel, c_d1, c_d2 = st.columns([2, 1, 1])
    with c_sel:
        indicador = st.selectbox("Indicador", options=sorted(list(DB_MACRO.keys())),
                                 index=None, placeholder="Selecionar série…")
    with c_d1:
        d_ini = st.date_input("Início", value=datetime(2020, 1, 1))
    with c_d2:
        d_fim = st.date_input("Fim", value=datetime.now())

    if indicador:
        info = DB_MACRO[indicador]
        df_macro = get_macro_data(indicador, info, start_date=d_ini, end_date=d_fim)
        if not df_macro.empty:
            csv = df_macro.to_csv(index=False).encode('utf-8')
            c_lbl, c_dl = st.columns([3, 1])
            with c_lbl:
                st.markdown(f'<div class="section-label">{indicador}</div>', unsafe_allow_html=True)
            with c_dl:
                st.download_button("↓ CSV", data=csv,
                                   file_name=f"{indicador.replace(' ', '_').lower()}.csv",
                                   mime='text/csv')

            last_val = df_macro['Valor'].iloc[-1]
            last_date = df_macro['Data'].iloc[-1]
            prev_val = df_macro['Valor'].iloc[-2] if len(df_macro) > 1 else last_val
            delta = last_val - prev_val
            delta_pct = (delta / prev_val * 100) if prev_val != 0 else 0
            d_color = "#00C853" if delta >= 0 else "#FF3D3D"
            d_sign = "+" if delta >= 0 else ""

            st.markdown(
                f'<div style="font-family:\'IBM Plex Mono\',monospace; margin: 8px 0 12px 0;">'
                f'  <span style="font-size:1.4rem; font-weight:700; color:#fff;">{fmt_num(last_val)}</span>'
                f'  <span style="font-size:0.7rem; color:{d_color}; margin-left:12px;">{d_sign}{fmt_num(delta)} ({d_sign}{fmt_num(delta_pct)}%)</span>'
                f'  <span style="font-size:0.65rem; color:#777; margin-left:8px;">{last_date}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            fig_macro = go.Figure()
            fig_macro.add_trace(go.Scatter(
                x=df_macro['Data'], y=df_macro['Valor'],
                mode='lines', line=dict(color='#FF9900', width=1.5), name=indicador
            ))
            apply_chart_layout(fig_macro, height=280)
            st.plotly_chart(fig_macro, use_container_width=True, config={'displayModeBar': False})

            st.dataframe(df_macro.iloc[::-1].reset_index(drop=True), hide_index=True,
                         use_container_width=False, width=380,
                         column_config={"Valor": st.column_config.NumberColumn(format="%.2f")})
        else:
            st.warning("Série não encontrada para os parâmetros selecionados.")
    st.stop()

# ──────────────────────────────────────────────
# 11. ABA: BACKTEST
# ──────────────────────────────────────────────

if aba_selecionada == "Backtest":
    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1.2])
    with col1:
        ticker_raw = st.text_input("Ticker", placeholder="ex: PETR4").upper().strip()
    with col2:
        data_ini = st.date_input("Início", value=datetime(2023, 1, 1))
    with col3:
        data_fim = st.date_input("Fim", value=datetime.now())
    with col4:
        bench_map = {"Ibovespa": "^BVSP", "S&P 500": "^GSPC"}
        bench_label = st.selectbox("Benchmark", options=list(bench_map.keys()), index=0)
        benchmark = bench_map[bench_label]

    if st.button("GERAR BACKTEST"):
        if not ticker_raw:
            st.error("Digite um ticker.")
            st.stop()
        ticker_bt = f"{ticker_raw}.SA" if (len(ticker_raw) >= 5 and "." not in ticker_raw and ticker_raw[-1].isdigit()) else ticker_raw
        try:
            bt_data = yf.download([ticker_bt, benchmark], start=data_ini, end=data_fim, auto_adjust=True)['Close']
            if bt_data.empty:
                st.warning("Sem dados.")
                st.stop()

            var_ticker = ((bt_data[ticker_bt].iloc[-1] / bt_data[ticker_bt].iloc[0]) - 1) * 100
            var_bench  = ((bt_data[benchmark].iloc[-1]  / bt_data[benchmark].iloc[0])  - 1) * 100
            rel = var_ticker - var_bench
            returns = bt_data.pct_change()
            vol_t = returns[ticker_bt].std() * (252 ** 0.5) * 100
            dd_t_min = ((bt_data[ticker_bt] / bt_data[ticker_bt].cummax()) - 1).min() * 100

            kpi_cols = st.columns(5)
            kpis = [
                ("RETORNO", f"{var_ticker:+.2f}%", var_ticker >= 0),
                (f"vs {bench_label.upper()}", f"{rel:+.2f}%", rel >= 0),
                ("VOL. ANUAL.", f"{vol_t:.1f}%", None),
                ("MAX DRAWDOWN", f"{dd_t_min:.2f}%", False),
                ("SHARPE (est.)", f"{(var_ticker/vol_t):.2f}x" if vol_t else "-", None),
            ]
            for col, (lbl, val, is_pos) in zip(kpi_cols, kpis):
                color = "#00C853" if is_pos is True else ("#FF3D3D" if is_pos is False else "#fff")
                col.markdown(
                    f'<div style="border:1px solid #1a1a1a; padding:10px 12px; margin-top:8px;">'
                    f'  <div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.55rem; color:#aaa; letter-spacing:2px; text-transform:uppercase;">{lbl}</div>'
                    f'  <div style="font-family:\'IBM Plex Mono\',monospace; font-size:1rem; font-weight:700; color:{color}; margin-top:4px;">{val}</div>'
                    f'</div>', unsafe_allow_html=True
                )

            df_norm = (bt_data / bt_data.iloc[0]) * 100
            fig_bt = go.Figure()
            fig_bt.add_trace(go.Scatter(x=df_norm.index, y=df_norm[ticker_bt],
                                        name=f"{ticker_bt} ({var_ticker:+.2f}%)",
                                        line=dict(color="#FFFFFF", width=1.5)))
            fig_bt.add_trace(go.Scatter(x=df_norm.index, y=df_norm[benchmark],
                                        name=f"{bench_label} ({var_bench:+.2f}%)",
                                        line=dict(color="#FF9900", width=1.2)))
            apply_chart_layout(fig_bt, "Performance Base 100", height=400, legend=True)
            st.plotly_chart(fig_bt, use_container_width=True, config={'displayModeBar': False})

            c_vol_col, c_dd_col = st.columns(2)
            vol_r_t = returns[ticker_bt].rolling(21).std() * (252 ** 0.5) * 100
            vol_r_b = returns[benchmark].rolling(21).std() * (252 ** 0.5) * 100
            with c_vol_col:
                fig_vol = go.Figure()
                fig_vol.add_trace(go.Scatter(x=vol_r_t.dropna().index, y=vol_r_t.dropna(), name=ticker_bt, line=dict(color="#fff", width=1.2)))
                fig_vol.add_trace(go.Scatter(x=vol_r_b.dropna().index, y=vol_r_b.dropna(), name=bench_label, line=dict(color="#FF9900", width=1.2)))
                apply_chart_layout(fig_vol, "Volatilidade Anualizada 21d", height=280, legend=True)
                st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})

            dd_t = (bt_data[ticker_bt] / bt_data[ticker_bt].cummax() - 1) * 100
            dd_b = (bt_data[benchmark] / bt_data[benchmark].cummax() - 1) * 100
            with c_dd_col:
                fig_dd = go.Figure()
                fig_dd.add_trace(go.Scatter(x=dd_t.index, y=dd_t, name=ticker_bt, line=dict(color="#fff", width=1),
                                            fill='tozeroy', fillcolor='rgba(255,255,255,0.04)'))
                fig_dd.add_trace(go.Scatter(x=dd_b.index, y=dd_b, name=bench_label, line=dict(color="#FF9900", width=1),
                                            fill='tozeroy', fillcolor='rgba(255,153,0,0.04)'))
                apply_chart_layout(fig_dd, "Drawdown (%)", height=280, legend=True)
                st.plotly_chart(fig_dd, use_container_width=True, config={'displayModeBar': False})

            st.markdown(f'<div class="section-label">RENTABILIDADE MENSAL — {ticker_bt}</div>', unsafe_allow_html=True)
            monthly_prices = bt_data[ticker_bt].resample('ME').last()
            first_price = bt_data[ticker_bt].iloc[0]
            m_ret = monthly_prices.pct_change() * 100
            if not m_ret.empty:
                m_ret.iloc[0] = ((monthly_prices.iloc[0] / first_price) - 1) * 100
            df_m = m_ret.to_frame()
            df_m['ano'] = df_m.index.year
            df_m['mes'] = df_m.index.month
            month_names = {1:'JAN',2:'FEV',3:'MAR',4:'ABR',5:'MAI',6:'JUN',7:'JUL',8:'AGO',9:'SET',10:'OUT',11:'NOV',12:'DEZ'}
            pivot_ret = df_m.pivot(index='ano', columns='mes', values=ticker_bt).rename(columns=month_names)
            cols_ordered = [month_names[i] for i in range(1, 13) if month_names[i] in pivot_ret.columns]
            pivot_ret = pivot_ret[cols_ordered]
            for year in pivot_ret.index:
                y_data = bt_data[ticker_bt][bt_data[ticker_bt].index.year == year]
                pivot_ret.loc[year, 'ANO'] = ((y_data.iloc[-1] / y_data.iloc[0]) - 1) * 100

            html_rent = ['<table class="rent-table"><tr><th>ANO</th>']
            for m in pivot_ret.columns:
                html_rent.append(f'<th>{m}</th>')
            html_rent.append('</tr>')
            for year in pivot_ret.index[::-1]:
                html_rent.append(f'<tr><td class="rent-year">{year}</td>')
                for col_name in pivot_ret.columns:
                    val = pivot_ret.loc[year, col_name]
                    if pd.isna(val):
                        html_rent.append('<td>-</td>')
                    else:
                        color = "#00C853" if val > 0 else ("#FF3D3D" if val < 0 else "#fff")
                        css = 'class="rent-total"' if col_name == "ANO" else ""
                        html_rent.append(f'<td {css} style="color:{color}">{val:.2f}%</td>')
                html_rent.append('</tr>')
            html_rent.append('</table>')
            st.markdown('<div class="table-scroll-wrapper">' + "".join(html_rent) + '</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="section-label" style="margin-top:16px;">ANUAL VS {bench_label.upper()}</div>', unsafe_allow_html=True)
            annual_comparison = []
            for yr in sorted(bt_data.index.year.unique(), reverse=True):
                yp = bt_data[bt_data.index.year == yr]
                t_r = ((yp[ticker_bt].iloc[-1] / yp[ticker_bt].iloc[0]) - 1) * 100
                b_r = ((yp[benchmark].iloc[-1]  / yp[benchmark].iloc[0])  - 1) * 100
                annual_comparison.append({"ano": yr, "ticker": t_r, "bench": b_r, "rel": t_r - b_r})
            html_a = [f'<table class="rent-table"><tr><th>ANO</th><th>{ticker_bt}</th><th>{bench_label}</th><th>RELATIVO</th></tr>']
            for row in annual_comparison:
                c_t = "#00C853" if row["ticker"] > 0 else "#FF3D3D"
                c_b = "#00C853" if row["bench"]  > 0 else "#FF3D3D"
                c_r = "#00C853" if row["rel"]    > 0 else "#FF3D3D"
                html_a.append(f'<tr><td class="rent-year">{row["ano"]}</td>'
                               f'<td style="color:{c_t}">{row["ticker"]:.2f}%</td>'
                               f'<td style="color:{c_b}">{row["bench"]:.2f}%</td>'
                               f'<td class="rent-total" style="color:{c_r}">{row["rel"]:.2f}%</td></tr>')
            html_a.append('</table>')
            st.markdown('<div class="table-scroll-wrapper">' + "".join(html_a) + '</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro: {e}")
    st.stop()

# ──────────────────────────────────────────────
# 12. ABA: BACKTEST PORTFÓLIO
# ──────────────────────────────────────────────

if aba_selecionada == "Backtest portfólio":
    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1.2])
    with col1:
        st.caption("Ativos e pesos abaixo")
    with col2:
        data_ini = st.date_input("Início", value=datetime(2023, 1, 1))
    with col3:
        data_fim = st.date_input("Fim", value=datetime.now())
    with col4:
        bench_map = {"Ibovespa": "^BVSP", "S&P 500": "^GSPC"}
        bench_label = st.selectbox("Benchmark", options=list(bench_map.keys()), index=0)
        benchmark = bench_map[bench_label]

    if "df_portfolio_input" not in st.session_state:
        st.session_state.df_portfolio_input = pd.DataFrame(columns=["Ticker", "Peso (%)"])
    edited_df = st.data_editor(st.session_state.df_portfolio_input, num_rows="dynamic",
                                use_container_width=True, hide_index=True)

    if st.button("GERAR BACKTEST PORTFÓLIO"):
        valid_rows = edited_df.dropna(subset=["Ticker", "Peso (%)"])
        valid_rows = valid_rows[valid_rows["Ticker"].astype(str).str.strip() != ""]
        valid_rows["Peso (%)"] = pd.to_numeric(valid_rows["Peso (%)"], errors='coerce').fillna(0)
        if valid_rows.empty:
            st.error("Adicione pelo menos um ativo.")
            st.stop()
        total_weight = valid_rows["Peso (%)"].sum()
        if not (99.9 <= total_weight <= 100.1):
            st.error(f"Soma dos pesos deve ser 100%. Atual: {total_weight:.2f}%")
            st.stop()

        tickers_list, weights_dict = [], {}
        for _, row in valid_rows.iterrows():
            t_raw = str(row["Ticker"]).upper().strip()
            t_fmt = f"{t_raw}.SA" if (len(t_raw) >= 5 and "." not in t_raw and t_raw[-1].isdigit()) else t_raw
            tickers_list.append(t_fmt)
            weights_dict[t_fmt] = row["Peso (%)"] / 100.0

        try:
            raw_data = yf.download(tickers_list + [benchmark], start=data_ini, end=data_fim, auto_adjust=True)['Close']
            if raw_data.empty:
                st.error("Dados não encontrados.")
                st.stop()

            daily_rets = raw_data.pct_change().fillna(0)
            portfolio_daily_ret = sum(daily_rets[t] * weights_dict[t] for t in tickers_list if t in daily_rets.columns)
            portfolio_price = (1 + portfolio_daily_ret).cumprod() * 100
            bt_data = pd.DataFrame({
                "PORTFOLIO": portfolio_price,
                benchmark: raw_data[benchmark]
            })
            ticker_bt = "PORTFOLIO"
            var_ticker = ((bt_data[ticker_bt].iloc[-1] / bt_data[ticker_bt].iloc[0]) - 1) * 100
            var_bench  = ((bt_data[benchmark].iloc[-1]  / bt_data[benchmark].iloc[0])  - 1) * 100

            _report_figs = []

            # ── Composição ──
            st.markdown('<div class="section-label">COMPOSIÇÃO DO PORTFÓLIO</div>', unsafe_allow_html=True)
            c_pie, c_tab = st.columns([1, 1])
            with c_pie:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(weights_dict.keys()),
                    values=list(weights_dict.values()),
                    hole=.4,
                    textposition='auto',
                    textinfo='percent+label',
                    textfont=dict(family='IBM Plex Mono', size=9),
                    marker=dict(line=dict(color='#0a0a0a', width=1))
                )])
                pie_layout = dict(**CHART_LAYOUT)
                pie_layout['height'] = 320
                pie_layout['margin'] = dict(t=8, b=8, l=8, r=8)
                fig_pie.update_layout(**pie_layout)
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
                _report_figs.append(("Composição do Portfólio", fig_pie))
            with c_tab:
                st.dataframe(valid_rows, hide_index=True, use_container_width=True)

            # ── Performance ──
            df_norm = (bt_data / bt_data.iloc[0]) * 100
            fig_bt = go.Figure()
            fig_bt.add_trace(go.Scatter(x=df_norm.index, y=df_norm[ticker_bt],
                                        name=f"PORTFÓLIO ({var_ticker:+.2f}%)", line=dict(color="#fff", width=1.5)))
            fig_bt.add_trace(go.Scatter(x=df_norm.index, y=df_norm[benchmark],
                                        name=f"{bench_label} ({var_bench:+.2f}%)", line=dict(color="#FF9900", width=1.2)))
            apply_chart_layout(fig_bt, "Performance Base 100", height=380, legend=True)
            st.plotly_chart(fig_bt, use_container_width=True, config={'displayModeBar': False})
            _report_figs.append(("Performance Base 100", fig_bt))

            # ── Vol + DD ──
            returns = bt_data.pct_change()
            c_vol_col, c_dd_col = st.columns(2)
            vol_t = returns[ticker_bt].rolling(21).std() * (252 ** 0.5) * 100
            vol_b = returns[benchmark].rolling(21).std() * (252 ** 0.5) * 100
            with c_vol_col:
                fig_vol = go.Figure()
                fig_vol.add_trace(go.Scatter(x=vol_t.dropna().index, y=vol_t.dropna(), name="Portfólio", line=dict(color="#fff", width=1.2)))
                fig_vol.add_trace(go.Scatter(x=vol_b.dropna().index, y=vol_b.dropna(), name=bench_label, line=dict(color="#FF9900", width=1.2)))
                apply_chart_layout(fig_vol, "Volatilidade 21d", height=280, legend=True)
                st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})
                _report_figs.append(("Volatilidade 21d", fig_vol))
            dd_t = (bt_data[ticker_bt] / bt_data[ticker_bt].cummax() - 1) * 100
            dd_b = (bt_data[benchmark] / bt_data[benchmark].cummax() - 1) * 100
            with c_dd_col:
                fig_dd = go.Figure()
                fig_dd.add_trace(go.Scatter(x=dd_t.index, y=dd_t, name="Portfólio", line=dict(color="#fff", width=1),
                                            fill='tozeroy', fillcolor='rgba(255,255,255,0.04)'))
                fig_dd.add_trace(go.Scatter(x=dd_b.index, y=dd_b, name=bench_label, line=dict(color="#FF9900", width=1),
                                            fill='tozeroy', fillcolor='rgba(255,153,0,0.04)'))
                apply_chart_layout(fig_dd, "Drawdown", height=280, legend=True)
                st.plotly_chart(fig_dd, use_container_width=True, config={'displayModeBar': False})
                _report_figs.append(("Drawdown", fig_dd))

            # ── Individual + Contribuição ──
            st.markdown('<div class="section-label" style="margin-top:8px;">DETALHAMENTO POR ATIVO</div>', unsafe_allow_html=True)
            c_ind, c_con = st.columns(2)
            with c_ind:
                df_assets_norm = (raw_data[tickers_list] / raw_data[tickers_list].iloc[0]) * 100
                fig_a = go.Figure()
                for t in tickers_list:
                    r = df_assets_norm[t].iloc[-1] - 100
                    fig_a.add_trace(go.Scatter(x=df_assets_norm.index, y=df_assets_norm[t],
                                               name=f"{t} ({r:+.1f}%)", line=dict(width=1), opacity=0.7))
                fig_a.add_trace(go.Scatter(x=portfolio_price.index, y=portfolio_price,
                                           name=f"PORTFÓLIO ({(portfolio_price.iloc[-1]-100):+.1f}%)",
                                           line=dict(color="#fff", width=2.5)))
                apply_chart_layout(fig_a, "Rentabilidade Individual (Base 100)", height=360, legend=True)
                fig_a.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5, font=dict(size=8)))
                st.plotly_chart(fig_a, use_container_width=True, config={'displayModeBar': False})
                _report_figs.append(("Rentabilidade Individual (Base 100)", fig_a))
            with c_con:
                contrib_data = [{"Ticker": t, "Contrib": ((raw_data[t].iloc[-1] / raw_data[t].iloc[0]) - 1) * weights_dict[t] * 100}
                                for t in tickers_list]
                df_contrib = pd.DataFrame(contrib_data).sort_values("Contrib", ascending=True)
                fig_c = go.Figure(go.Bar(
                    x=df_contrib["Contrib"], y=df_contrib["Ticker"], orientation='h',
                    marker=dict(color=["#00C853" if v >= 0 else "#FF3D3D" for v in df_contrib["Contrib"]]),
                    text=[f"{v:+.2f}pp" for v in df_contrib["Contrib"]],
                    textposition='auto', textfont=dict(size=9, family='IBM Plex Mono')
                ))
                apply_chart_layout(fig_c, "Contribuição (p.p.)", height=360)
                st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})
                _report_figs.append(("Contribuição (p.p.)", fig_c))

            # ── Rentabilidade mensal ──
            st.markdown('<div class="section-label" style="margin-top:8px;">RENTABILIDADE MENSAL — PORTFÓLIO</div>', unsafe_allow_html=True)
            monthly_prices = bt_data[ticker_bt].resample('ME').last()
            first_price = bt_data[ticker_bt].iloc[0]
            m_ret = monthly_prices.pct_change() * 100
            if not m_ret.empty:
                m_ret.iloc[0] = ((monthly_prices.iloc[0] / first_price) - 1) * 100
            df_m = m_ret.to_frame(); df_m['ano'] = df_m.index.year; df_m['mes'] = df_m.index.month
            month_names = {1:'JAN',2:'FEV',3:'MAR',4:'ABR',5:'MAI',6:'JUN',7:'JUL',8:'AGO',9:'SET',10:'OUT',11:'NOV',12:'DEZ'}
            pivot_ret = df_m.pivot(index='ano', columns='mes', values=ticker_bt).rename(columns=month_names)
            cols_ordered = [month_names[i] for i in range(1, 13) if month_names[i] in pivot_ret.columns]
            pivot_ret = pivot_ret[cols_ordered]
            for year in pivot_ret.index:
                y_data = bt_data[ticker_bt][bt_data[ticker_bt].index.year == year]
                pivot_ret.loc[year, 'ANO'] = ((y_data.iloc[-1] / y_data.iloc[0]) - 1) * 100
            html_rent = ['<table class="rent-table"><tr><th>ANO</th>'] + [f'<th>{m}</th>' for m in pivot_ret.columns] + ['</tr>']
            for year in pivot_ret.index[::-1]:
                html_rent.append(f'<tr><td class="rent-year">{year}</td>')
                for col_name in pivot_ret.columns:
                    val = pivot_ret.loc[year, col_name]
                    if pd.isna(val): html_rent.append('<td>-</td>')
                    else:
                        color = "#00C853" if val > 0 else "#FF3D3D"
                        css = 'class="rent-total"' if col_name == "ANO" else ""
                        html_rent.append(f'<td {css} style="color:{color}">{val:.2f}%</td>')
                html_rent.append('</tr>')
            html_rent.append('</table>')
            rent_table_html = "".join(html_rent)
            st.markdown('<div class="table-scroll-wrapper">' + rent_table_html + '</div>', unsafe_allow_html=True)

            # ── Gerar relatório HTML para download ──
            report_css = (
                "body { background:#0a0a0a; color:#e0e0e0; font-family:'IBM Plex Mono',monospace; margin:20px; padding:20px; }\n"
                "h1 { color:#FF9900; font-size:1.2rem; letter-spacing:3px; border-bottom:1px solid #FF9900; padding-bottom:8px; margin-bottom:4px; }\n"
                "h2 { color:#aaa; font-size:0.7rem; letter-spacing:2px; text-transform:uppercase; margin-top:32px; margin-bottom:8px; border-bottom:1px solid #1a1a1a; padding-bottom:4px; }\n"
                ".meta { font-size:0.65rem; color:#777; margin-bottom:20px; }\n"
                ".kpi-row { display:flex; gap:12px; margin:16px 0 24px 0; flex-wrap:wrap; }\n"
                ".kpi-box { border:1px solid #1a1a1a; padding:10px 16px; min-width:140px; }\n"
                ".kpi-label { font-size:0.55rem; color:#aaa; letter-spacing:2px; text-transform:uppercase; }\n"
                ".kpi-val { font-size:1rem; font-weight:700; margin-top:4px; }\n"
                ".chart-container { margin:12px 0 24px 0; }\n"
                ".rent-table { width:100%; border-collapse:collapse; font-family:'IBM Plex Mono',monospace; font-size:0.68rem; border:1px solid #1a1a1a; margin:12px 0; }\n"
                ".rent-table th { background:#0d0d0d; color:#FF9900; padding:6px 4px; border:1px solid #1a1a1a; text-transform:uppercase; font-size:0.58rem; letter-spacing:1px; text-align:center; }\n"
                ".rent-table td { padding:5px 4px; border:1px solid #111; color:#e0e0e0; text-align:center; font-variant-numeric:tabular-nums; }\n"
                ".rent-year { background:#0d0d0d !important; font-weight:700; color:#e0e0e0 !important; text-align:left !important; padding-left:8px !important; }\n"
                ".rent-total { background:#0d0d0d; font-weight:700; }\n"
                ".comp-table { border-collapse:collapse; font-size:0.72rem; margin:8px 0 16px 0; }\n"
                ".comp-table th { color:#FF9900; text-align:left; padding:6px 12px; border-bottom:1px solid #FF9900; font-size:0.6rem; letter-spacing:1px; text-transform:uppercase; }\n"
                ".comp-table td { padding:5px 12px; border-bottom:1px solid #111; color:#e0e0e0; }\n"
                "@media print { body { -webkit-print-color-adjust:exact !important; print-color-adjust:exact !important; } }\n"
            )

            rel_val = var_ticker - var_bench
            kpi_html = (
                '<div class="kpi-row">'
                '<div class="kpi-box"><div class="kpi-label">RETORNO PORTFÓLIO</div>'
                f'<div class="kpi-val" style="color:{"#00C853" if var_ticker>=0 else "#FF3D3D"}">{var_ticker:+.2f}%</div></div>'
                f'<div class="kpi-box"><div class="kpi-label">RETORNO {bench_label.upper()}</div>'
                f'<div class="kpi-val" style="color:{"#00C853" if var_bench>=0 else "#FF3D3D"}">{var_bench:+.2f}%</div></div>'
                '<div class="kpi-box"><div class="kpi-label">RELATIVO</div>'
                f'<div class="kpi-val" style="color:{"#00C853" if rel_val>=0 else "#FF3D3D"}">{rel_val:+.2f}%</div></div>'
                '</div>'
            )

            comp_html = '<table class="comp-table"><tr><th>TICKER</th><th>PESO</th></tr>'
            for tk, w in weights_dict.items():
                comp_html += f'<tr><td style="color:#fff; font-weight:700;">{tk}</td><td>{w*100:.1f}%</td></tr>'
            comp_html += '</table>'

            charts_html = ""
            plotly_js_included = False
            for chart_title, fig in _report_figs:
                include_js = 'cdn' if not plotly_js_included else False
                plotly_js_included = True
                fig_for_report = go.Figure(fig)
                fig_for_report.update_layout(paper_bgcolor='#0a0a0a', plot_bgcolor='#0a0a0a')
                chart_div = pio.to_html(fig_for_report, full_html=False, include_plotlyjs=include_js)
                charts_html += f'<h2>{chart_title}</h2><div class="chart-container">{chart_div}</div>'

            report_full_html = (
                '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                '<title>Backtest Portfólio</title>\n'
                f'<style>\n{report_css}</style>\n</head>\n<body>\n'
                '<h1>BACKTEST PORTFÓLIO</h1>\n'
                f'<div class="meta">Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")} &nbsp;|&nbsp; '
                f'Período: {data_ini.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")} &nbsp;|&nbsp; '
                f'Benchmark: {bench_label}</div>\n'
                f'{kpi_html}\n'
                '<h2>COMPOSIÇÃO</h2>\n'
                f'{comp_html}\n'
                f'{charts_html}\n'
                '<h2>RENTABILIDADE MENSAL</h2>\n'
                f'{rent_table_html}\n'
                '</body>\n</html>'
            )

            st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
            st.download_button(
                "↓ EXPORTAR RELATÓRIO",
                data=report_full_html.encode('utf-8'),
                file_name=f"backtest_portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html"
            )

        except Exception as e:
            st.error(f"Erro: {e}")
    st.stop()

# ──────────────────────────────────────────────
# 13. ABA: CALENDÁRIO
# ──────────────────────────────────────────────

if aba_selecionada == "Calendário econômico":
    components.html(
        """<iframe src="https://sslecal2.investing.com?ecoDayBackground=%230a0a0a&defaultFont=%230a0a0a&innerBorderColor=%231a1a1a&borderColor=%231a1a1a&ecoDayFontColor=%23ffffff&columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&features=datepicker,timeselector,filters&countries=17,32,37,5,35,4,72&calType=day&timeZone=12&lang=12"
width="100%" height="650" frameborder="0" allowtransparency="true" marginwidth="0" marginheight="0"></iframe>""",
        height=700, scrolling=True
    )
    st.stop()

# ──────────────────────────────────────────────
# 14. ABAS PRINCIPAIS: COBERTURA / ACOMP / ÍNDICES
# ──────────────────────────────────────────────

cols_base = ["HOJE", "30D", "6M", "12M", "YTD", "5A"]
df_p = pd.DataFrame()

if aba_selecionada == "Cobertura":
    headers = ["Ticker", "Preço", "Rec.", "Alvo", "Upside"] + cols_base
    t_list = sorted(list(COBERTURA.keys()))

elif aba_selecionada == "Carteira pessoal":
    if not APORTES_USUARIO:
        st.info("Adicione aportes em APORTES_USUARIO para visualizar a carteira.")
        st.stop()

    df_aportes = pd.DataFrame(APORTES_USUARIO)
    df_aportes['data'] = pd.to_datetime(df_aportes['data'])
    start_date = df_aportes['data'].min()

    tickers_carteira = df_aportes['ticker'].unique().tolist()
    if "^BVSP" not in tickers_carteira:
        tickers_carteira.append("^BVSP")

    try:
        valid_tickers = [t for t in tickers_carteira if t in master_data.columns.levels[0]]
        prices = pd.DataFrame({t: master_data[t]['Close'] for t in valid_tickers})
        prices.index = prices.index.tz_localize(None)
        prices = prices.sort_index().loc[start_date:].ffill()
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        st.stop()

    all_dates = prices.index
    df_qtd = pd.DataFrame(0, index=all_dates, columns=[t for t in tickers_carteira if t != "^BVSP"])
    for _, row in df_aportes.iterrows():
        idx_loc = df_qtd.index.searchsorted(row['data'])
        if idx_loc < len(df_qtd):
            df_qtd.iloc[idx_loc:, df_qtd.columns.get_loc(row['ticker'])] += row['qtd']

    cols_ativos = [t for t in tickers_carteira if t != "^BVSP" and t in prices.columns]
    pct_change = prices[cols_ativos].pct_change().fillna(0)
    df_qtd_aligned = df_qtd[cols_ativos].reindex(prices.index).ffill().fillna(0)
    pos_yesterday = (prices[cols_ativos].shift(1) * df_qtd_aligned.shift(1)).fillna(0)
    total_yesterday = pos_yesterday.sum(axis=1)
    weights = pos_yesterday.div(total_yesterday, axis=0).fillna(0)
    portfolio_ret = (weights * pct_change).sum(axis=1)
    portfolio_idx = (1 + portfolio_ret).cumprod() * 100
    ibov_idx = (1 + prices["^BVSP"].pct_change().fillna(0)).cumprod() * 100 if "^BVSP" in prices.columns else pd.Series(100, index=portfolio_idx.index)
    if len(portfolio_idx) > 0:
        portfolio_idx = (portfolio_idx / portfolio_idx.iloc[0]) * 100
        ibov_idx = (ibov_idx / ibov_idx.iloc[0]) * 100

    qtd_atual = df_qtd_aligned.iloc[-1]
    qtd_atual = qtd_atual[qtd_atual > 0]
    t_list_cart = qtd_atual.index.tolist()

    pos_data = []
    total_portfolio_val = 0
    for t in t_list_cart:
        try:
            p = float(prices[t].iloc[-1])
            q = float(qtd_atual[t])
            val = p * q
            cl = prices[t].dropna()
            pos_data.append({
                "Ticker": t, "Preço": p, "Total": val,
                "HOJE": calc_variation(cl, 1), "30D": calc_variation(cl, 21),
                "6M": calc_variation(cl, 126), "12M": calc_variation(cl, 252),
                "YTD": calc_variation(cl, ytd=True), "5A": calc_variation(cl, 1260)
            })
            total_portfolio_val += val
        except Exception:
            continue

    df_pos_table = pd.DataFrame(pos_data)
    if not df_pos_table.empty:
        df_pos_table["Peso %"] = (df_pos_table["Total"] / total_portfolio_val) * 100
        df_pos_table = df_pos_table.sort_values("Peso %", ascending=False)

        html_cart = ['<div class="desktop-view"><table class="bb-table"><thead><tr>',
                     '<th>TICKER</th><th>PREÇO</th><th>TOTAL</th><th>PESO</th>',
                     '<th>HOJE</th><th>30D</th><th>6M</th><th>12M</th><th>YTD</th><th>5A</th></tr></thead><tbody>']
        html_mob = ['<div class="mobile-view">']
        for _, row in df_pos_table.iterrows():
            sym = "R$ "
            t = row["Ticker"]
            peso_fmt = f'<span style="color:#fff">{fmt_num(row["Peso %"])}%</span>'
            html_cart.append(f'<tr><td><span class="ticker-sym">{t}</span></td>'
                              f'<td>{fmt_price(row["Preço"], sym)}</td>'
                              f'<td>{fmt_price(row["Total"], sym)}</td>'
                              f'<td>{peso_fmt}</td>')
            for col_name in ["HOJE", "30D", "6M", "12M", "YTD", "5A"]:
                html_cart.append(f'<td>{fmt_pct(row[col_name])}</td>')
            html_cart.append('</tr>')
            f_p2 = fmt_num(row["Preço"])
            html_mob.append(f'<details><summary>'
                             f'<div class="mob-header-left"><span class="mob-ticker">{t}</span></div>'
                             f'<div class="mob-header-right"><span class="mob-price">{sym}{f_p2}</span>'
                             f'<span class="mob-today">{fmt_pct(row["HOJE"])}</span></div></summary>'
                             f'<div class="mob-content"><div class="mob-grid">'
                             f'<div class="mob-item"><span class="mob-label">TOTAL</span><span class="mob-val">{fmt_price(row["Total"], sym)}</span></div>'
                             f'<div class="mob-item"><span class="mob-label">PESO</span><span class="mob-val" style="color:#fff">{fmt_num(row["Peso %"])}%</span></div>')
            for col_name in ["30D", "6M", "12M", "YTD", "5A"]:
                html_mob.append(f'<div class="mob-item"><span class="mob-label">{col_name}</span><span class="mob-val">{fmt_pct(row[col_name])}</span></div>')
            html_mob.append('</div></div></details>')
        html_cart.append('</tbody></table></div>')
        html_mob.append('</div>')
        st.markdown("".join(html_cart) + "".join(html_mob), unsafe_allow_html=True)

    var_cart = portfolio_idx.iloc[-1] - 100
    var_ibov = ibov_idx.iloc[-1] - 100
    port_hoje = portfolio_ret.iloc[-1] * 100
    ibov_hoje = prices["^BVSP"].pct_change().iloc[-1] * 100 if "^BVSP" in prices.columns else 0.0
    dif = port_hoje - ibov_hoje

    kpi_data = [
        ("HOJE CARTEIRA", f"{port_hoje:+.2f}%", port_hoje >= 0),
        ("HOJE IBOV", f"{ibov_hoje:+.2f}%", ibov_hoje >= 0),
        ("ALFA HOJE", f"{dif:+.2f}%", dif >= 0),
        ("RETORNO TOTAL", f"{var_cart:+.2f}%", var_cart >= 0),
        ("vs IBOVESPA", f"{(var_cart - var_ibov):+.2f}%", (var_cart - var_ibov) >= 0),
        ("PATRIMÔNIO", f"R$ {fmt_num(total_portfolio_val)}", None),
    ]
    kpi_cols = st.columns(6)
    for col, (lbl, val, is_pos) in zip(kpi_cols, kpi_data):
        color = "#00C853" if is_pos is True else ("#FF3D3D" if is_pos is False else "#FF9900")
        col.markdown(
            f'<div style="border:1px solid #1a1a1a; padding:8px 10px; margin-top:10px;">'
            f'  <div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.52rem; color:#aaa; letter-spacing:2px;">{lbl}</div>'
            f'  <div style="font-family:\'IBM Plex Mono\',monospace; font-size:0.9rem; font-weight:700; color:{color}; margin-top:3px;">{val}</div>'
            f'</div>', unsafe_allow_html=True
        )

    st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig_perf = go.Figure()
        fig_perf.add_trace(go.Scatter(x=portfolio_idx.index, y=portfolio_idx, name=f"Carteira ({var_cart:+.2f}%)", line=dict(color="#fff", width=1.5)))
        fig_perf.add_trace(go.Scatter(x=ibov_idx.index, y=ibov_idx, name=f"Ibovespa ({var_ibov:+.2f}%)", line=dict(color="#FF9900", width=1.2)))
        apply_chart_layout(fig_perf, "Rentabilidade vs Ibovespa", height=320, legend=True)
        st.plotly_chart(fig_perf, use_container_width=True, config={'displayModeBar': False})
    with c2:
        net_worth_series = (df_qtd_aligned * prices[cols_ativos]).sum(axis=1)
        fig_nw = go.Figure()
        fig_nw.add_trace(go.Bar(x=net_worth_series.index, y=net_worth_series,
                                marker_color="#FF9900", marker_line_width=0))
        apply_chart_layout(fig_nw, "Evolução do Patrimônio", height=320)
        st.plotly_chart(fig_nw, use_container_width=True, config={'displayModeBar': False})

    c_vol, c_dd = st.columns(2)
    with c_vol:
        vol_cart = portfolio_ret.rolling(21).std() * (252 ** 0.5) * 100
        vol_ibov = prices["^BVSP"].pct_change().rolling(21).std() * (252 ** 0.5) * 100 if "^BVSP" in prices.columns else pd.Series(0, index=vol_cart.index)
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=vol_cart.index, y=vol_cart, name="Carteira", line=dict(color="#fff", width=1.5)))
        fig_vol.add_trace(go.Scatter(x=vol_ibov.index, y=vol_ibov, name="Ibov", line=dict(color="#FF9900", width=1.2)))
        apply_chart_layout(fig_vol, "Volatilidade 21d", height=280, legend=True)
        st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})
    with c_dd:
        dd_cart = (portfolio_idx / portfolio_idx.cummax() - 1) * 100
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(x=dd_cart.index, y=dd_cart, line=dict(color="#FF3D3D", width=1.5),
                                    fill='tozeroy', fillcolor='rgba(255,61,61,0.06)'))
        apply_chart_layout(fig_dd, "Drawdown", height=280)
        st.plotly_chart(fig_dd, use_container_width=True, config={'displayModeBar': False})

    c_sharpe, c_setor = st.columns(2)
    with c_sharpe:
        info_selic = DB_MACRO["Taxa Selic"]
        df_selic = get_macro_data("Taxa Selic", info_selic, start_date=start_date)
        if not df_selic.empty:
            df_selic['Data'] = pd.to_datetime(df_selic['Data'], dayfirst=True)
            df_selic = df_selic.set_index('Data').reindex(portfolio_ret.index).ffill().fillna(0)
            rf_daily = (1 + df_selic['Valor'] / 100) ** (1/252) - 1
        else:
            rf_daily = pd.Series(0, index=portfolio_ret.index)
        excess_ret = portfolio_ret - rf_daily
        sharpe_rolling = (excess_ret.rolling(30).mean() / portfolio_ret.rolling(30).std()) * (252 ** 0.5)
        fig_sharpe = go.Figure()
        fig_sharpe.add_trace(go.Scatter(x=sharpe_rolling.index, y=sharpe_rolling, line=dict(color="#fff", width=1.5)))
        apply_chart_layout(fig_sharpe, "Índice Sharpe 30d Rolling", height=280)
        st.plotly_chart(fig_sharpe, use_container_width=True, config={'displayModeBar': False})

    with c_setor:
        MAPA_SETORES_GRAFICO = {
            "WEGE3.SA": "Capital Goods", "EQTL3.SA": "Utilities", "MULT3.SA": "Malls",
            "RENT3.SA": "Transport", "LEVE3.SA": "Capital Goods", "ITUB3.SA": "Banks",
            "EGIE3.SA": "Utilities", "RADL3.SA": "Retail", "SMFT3.SA": "Retail",
            "MDIA3.SA": "Agribusiness", "BBSE3.SA": "Banks", "LREN3.SA": "Retail",
            "BPAC3.SA": "Banks", "VIVT3.SA": "Telecom", "ASAI3.SA": "Retail",
            "UNIP3.SA": "Chemicals", "PSSA3.SA": "Banks", "PRIO3.SA": "Oil & Gas",
            "VULC3.SA": "Retail", "VALE3.SA": "Mining", "SBSP3.SA": "Utilities",
        }
        current_prices = prices.iloc[-1]
        alloc_data = []
        total_val = 0
        for t, q in qtd_atual.items():
            if t in current_prices:
                val = current_prices[t] * q
                alloc_data.append({"Setor": MAPA_SETORES_GRAFICO.get(t, "Outros"), "Valor": val})
                total_val += val
        if alloc_data:
            df_sector = pd.DataFrame(alloc_data).groupby("Setor")["Valor"].sum().sort_values(ascending=True)
            df_sector_pct = (df_sector / total_val) * 100
            fig_sec = go.Figure(go.Bar(
                x=df_sector_pct.values, y=df_sector_pct.index, orientation='h',
                marker=dict(color='#FF9900', line=dict(width=0)),
                text=[f"{v:.1f}%" for v in df_sector_pct.values],
                textposition='auto', textfont=dict(size=9, family='IBM Plex Mono', color='#fff')
            ))
            apply_chart_layout(fig_sec, "Alocação por Setor", height=280)
            fig_sec.update_layout(xaxis=dict(showgrid=False, showticklabels=False, fixedrange=True),
                                   yaxis=dict(showgrid=False, tickfont=dict(color='#aaa', size=9), fixedrange=True))
            st.plotly_chart(fig_sec, use_container_width=True, config={'displayModeBar': False})

    st.markdown('<div class="section-label" style="margin-top:8px;">RENTABILIDADE DETALHADA</div>', unsafe_allow_html=True)
    c_hist, c_mes = st.columns(2)
    with c_hist:
        fig_ah = go.Figure()
        for t in t_list_cart:
            idx_in = df_qtd_aligned[t] > 0
            if idx_in.any():
                first_date = idx_in.idxmax()
                ap = prices[t].loc[first_date:]
                if not ap.empty:
                    ai = (ap / ap.iloc[0]) * 100
                    fig_ah.add_trace(go.Scatter(x=ai.index, y=ai, name=f"{t} ({(ai.iloc[-1]-100):+.1f}%)", line=dict(width=1.2), opacity=0.8))
        apply_chart_layout(fig_ah, "Desde o 1º Aporte (Base 100)", height=600, legend=True)
        fig_ah.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.08, xanchor="center", x=0.5, font=dict(size=8)))
        st.plotly_chart(fig_ah, use_container_width=True, config={'displayModeBar': False})

    with c_mes:
        if len(prices) > 0:
            mes_atual = prices.index[-1].month
            ano_atual = prices.index[-1].year
            mascara_mes = (prices.index.month == mes_atual) & (prices.index.year == ano_atual)
            if mascara_mes.any():
                precos_mes = prices[mascara_mes]
                idx_ant = prices.index.get_loc(precos_mes.index[0]) - 1
                base_price = prices.iloc[idx_ant][cols_ativos] if idx_ant >= 0 else precos_mes.iloc[0][cols_ativos]
                mtd_rets = (precos_mes.iloc[-1][cols_ativos] / base_price - 1) * 100
                mtd_rets = mtd_rets[mtd_rets.index.isin(t_list_cart)].dropna().sort_values(ascending=True)
                if not mtd_rets.empty:
                    fig_mtd = go.Figure(go.Bar(
                        x=mtd_rets.values, y=mtd_rets.index, orientation='h',
                        marker=dict(color=["#00C853" if v >= 0 else "#FF3D3D" for v in mtd_rets.values], line=dict(width=0)),
                        text=[f"{v:+.2f}%" for v in mtd_rets.values],
                        textposition='auto', textfont=dict(size=9, family='IBM Plex Mono', color='#fff')
                    ))
                    apply_chart_layout(fig_mtd, "Rentabilidade no Mês", height=600)
                    st.plotly_chart(fig_mtd, use_container_width=True, config={'displayModeBar': False})

    st.markdown('<div class="section-label" style="margin-top:8px;">RENTABILIDADE MENSAL — CARTEIRA vs IBOVESPA</div>', unsafe_allow_html=True)
    ret_daily_port = portfolio_ret
    ret_daily_ibov = prices["^BVSP"].pct_change().fillna(0) if "^BVSP" in prices.columns else pd.Series(0, index=portfolio_ret.index)
    ret_m_port = ret_daily_port.resample('ME').apply(lambda x: (1 + x).prod() - 1) * 100
    ret_m_ibov = ret_daily_ibov.resample('ME').apply(lambda x: (1 + x).prod() - 1) * 100

    def make_pivot(series):
        df = series.to_frame(name='ret')
        df['ano'] = df.index.year; df['mes'] = df.index.month
        return df.pivot(index='ano', columns='mes', values='ret')

    piv_port = make_pivot(ret_m_port)
    piv_ibov = make_pivot(ret_m_ibov)
    month_names = {1:'JAN',2:'FEV',3:'MAR',4:'ABR',5:'MAI',6:'JUN',7:'JUL',8:'AGO',9:'SET',10:'OUT',11:'NOV',12:'DEZ'}
    html_rent = ['<table class="rent-table"><tr><th>ANO</th>']
    for i in range(1, 13): html_rent.append(f'<th>{month_names[i]}</th>')
    html_rent.append('<th>ANO</th><th>ACUM.</th></tr>')

    for y in sorted(piv_port.index, reverse=True):
        d_p_y = ret_daily_port[ret_daily_port.index.year == y]
        d_i_y = ret_daily_ibov[ret_daily_ibov.index.year == y]
        total_y_port = ((1 + d_p_y).prod() - 1) * 100
        total_y_ibov = ((1 + d_i_y).prod() - 1) * 100
        d_p_cum = ret_daily_port[ret_daily_port.index <= d_p_y.index[-1]]
        d_i_cum = ret_daily_ibov[ret_daily_ibov.index <= d_i_y.index[-1]]
        cum_port = ((1 + d_p_cum).prod() - 1) * 100
        cum_ibov = ((1 + d_i_cum).prod() - 1) * 100

        for label, piv, total, cum, row_color in [
            (f"Carteira {y}", piv_port, total_y_port, cum_port, "#e0e0e0"),
            (f"Ibovespa {y}", piv_ibov, total_y_ibov, cum_ibov, "#FF9900"),
        ]:
            html_rent.append(f'<tr><td style="text-align:left; font-weight:700; color:{row_color}; border:1px solid #1a1a1a; padding-left:8px; font-size:0.65rem;">{label}</td>')
            for m in range(1, 13):
                val = piv.loc[y, m] if (y in piv.index and m in piv.columns) else np.nan
                if pd.isna(val) or (y == datetime.now().year and m > datetime.now().month):
                    html_rent.append('<td>-</td>')
                else:
                    color = "#00C853" if val > 0 else "#FF3D3D"
                    html_rent.append(f'<td style="color:{color}">{val:.2f}%</td>')
            c_a = "#00C853" if total > 0 else "#FF3D3D"
            c_c = "#00C853" if cum   > 0 else "#FF3D3D"
            html_rent.append(f'<td style="font-weight:700; color:{c_a}">{total:.2f}%</td>')
            html_rent.append(f'<td style="font-weight:700; color:{c_c}">{cum:.2f}%</td></tr>')

    html_rent.append('</table>')
    st.markdown('<div class="table-scroll-wrapper">' + "".join(html_rent) + '</div>', unsafe_allow_html=True)
    st.stop()

elif aba_selecionada == "Índices":
    headers = ["Ticker", "Preço"] + cols_base
    t_list = INDICES_LIST

else:  # Acompanhamentos
    headers = ["Ticker", "Preço"] + cols_base
    t_list = []
    for s, ticks in SETORES_ACOMPANHAMENTO.items():
        t_list.append({"setor": s})
        t_list.extend(ticks)

# ──────────────────────────────────────────────
# 15. TABELA GENÉRICA (Cobertura / Acomp / Índices)
# ──────────────────────────────────────────────

tickers_da_aba = [tk for tk in t_list if isinstance(tk, str)]

with st.popover("↗ GRÁFICOS"):
    col_pop1, col_pop2 = st.columns(2)
    for i, tk in enumerate(tickers_da_aba):
        target_col = col_pop1 if i % 2 == 0 else col_pop2
        if target_col.button(tk, key=f"btn_{tk}", use_container_width=True):
            exibir_grafico_popup(tk, master_data)

html_d = ['<div class="desktop-view"><div class="table-scroll-wrapper"><table class="bb-table"><thead><tr>']
for h in headers:
    html_d.append(f'<th>{h.upper()}</th>')
html_d.append('</tr></thead><tbody>')

html_m = ['<div class="mobile-view">']

for t in t_list:
    if isinstance(t, dict):
        sn = t["setor"].upper()
        html_d.append(f'<tr class="sector-row"><td colspan="{len(headers)}" style="letter-spacing:2px; color:#FF9900;">{sn}</td></tr>')
        html_m.append(f'<div class="mob-sector">{sn}</div>')
        continue

    if t not in master_data.columns.levels[0]:
        continue
    try:
        cl = master_data[t]['Close'].dropna()
        if cl.empty:
            continue
        p = float(cl.iloc[-1])
        sym = "R$ " if (t == "^BVSP" or ".SA" in t) else ""
        v_h   = calc_variation(cl, 1)
        v_30  = calc_variation(cl, 21)
        v_6m  = calc_variation(cl, 126)
        v_12  = calc_variation(cl, 252)
        v_ytd = calc_variation(cl, ytd=True)
        v_5a  = calc_variation(cl, 1260)

        html_d.append(f'<tr><td><span class="ticker-sym">{t}</span></td><td>{fmt_price(p, sym)}</td>')
        if aba_selecionada == "Cobertura":
            rec = COBERTURA[t]["Rec"]
            alv = COBERTURA[t]["Alvo"]
            upside = (alv / p - 1) * 100
            rec_c = rec_class(rec)
            html_d.append(f'<td><span class="{rec_c}">{rec}</span></td>'
                          f'<td>{fmt_price(alv, sym)}</td>'
                          f'<td>{fmt_pct(upside)}</td>')
        for val in [v_h, v_30, v_6m, v_12, v_ytd, v_5a]:
            html_d.append(f'<td>{fmt_pct(val)}</td>')
        html_d.append('</tr>')

        f_p2 = fmt_num(p)
        html_m.append(f'<details><summary>'
                       f'<div class="mob-header-left"><span class="mob-ticker">{t}</span></div>'
                       f'<div class="mob-header-right"><span class="mob-price">{sym}{f_p2}</span>'
                       f'<span class="mob-today">{fmt_pct(v_h)}</span></div></summary>'
                       f'<div class="mob-content"><div class="mob-grid">')
        if aba_selecionada == "Cobertura":
            rec = COBERTURA[t]["Rec"]
            alv = COBERTURA[t]["Alvo"]
            upside = (alv / p - 1) * 100
            rec_c = rec_class(rec)
            html_m.append(f'<div class="mob-item"><span class="mob-label">REC</span><span class="mob-val"><span class="{rec_c}">{rec}</span></span></div>'
                           f'<div class="mob-item"><span class="mob-label">ALVO</span><span class="mob-val">{fmt_price(alv, sym)}</span></div>'
                           f'<div class="mob-item"><span class="mob-label">UPSIDE</span><span class="mob-val">{fmt_pct(upside)}</span></div>')
        for lbl, val in [("30D", v_30), ("6M", v_6m), ("12M", v_12), ("YTD", v_ytd), ("5A", v_5a)]:
            html_m.append(f'<div class="mob-item"><span class="mob-label">{lbl}</span><span class="mob-val">{fmt_pct(val)}</span></div>')
        html_m.append('</div></div></details>')
    except Exception:
        continue

html_d.append('</tbody></table></div></div>')
html_m.append('</div>')
st.markdown("".join(html_d) + "".join(html_m), unsafe_allow_html=True)
