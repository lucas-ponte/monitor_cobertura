import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURAÇÃO E CSS
st.set_page_config(page_title="DASHBOARD", layout="wide")

# Inicialização do session_state
if "ticker_selecionado" not in st.session_state:
    st.session_state.ticker_selecionado = None
if "periodo_grafico" not in st.session_state:
    st.session_state.periodo_grafico = "12M"
if "aba_ativa" not in st.session_state:
    st.session_state.aba_ativa = "Cobertura"

hora_atual = datetime.now().strftime("%H:%M")

# FUNÇÃO DO POPUP CENTRALIZADO
@st.dialog("Gráfico de Performance", width="large")
def exibir_grafico_popup(t_sel, data):
    per_map = {"30D": 21, "6M": 126, "12M": 252, "5A": 1260, "YTD": "ytd"}
    nova_selecao = st.pills("Período", options=list(per_map.keys()), key="pills_popup", default=st.session_state.periodo_grafico)
    if nova_selecao:
        st.session_state.periodo_grafico = nova_selecao
    
    h_raw = data[t_sel]['Close'].dropna()
    p_sel = st.session_state.periodo_grafico
    days = per_map.get(p_sel, 252)
    df_plot = h_raw.loc[f"{datetime.now().year}-01-01":] if days == "ytd" else (h_raw.iloc[-days:] if len(h_raw) >= days else h_raw)
    
    if not df_plot.empty:
        perf = ((df_plot.iloc[-1] / df_plot.iloc[0]) - 1) * 100
        color = "#00FF00" if perf >= 0 else "#FF4B4B"
        
        y_min = df_plot.min()
        y_max = df_plot.max()
        padding = (y_max - y_min) * 0.05 if y_max != y_min else y_min * 0.05
        
        st.markdown(f"### {t_sel} | {perf:+.2f}%")
        fig = go.Figure(go.Scatter(
            x=df_plot.index, 
            y=df_plot.values, 
            line=dict(color=color, width=2), 
            fill='tozeroy', 
            fillcolor=f"rgba({ '0,255,0' if perf >=0 else '255,75,75' }, 0.02)"
        ))
        
        fig.update_layout(
            template="plotly_dark", 
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)', 
            height=400, 
            margin=dict(l=0, r=0, t=10, b=0), 
            xaxis=dict(showgrid=False), 
            yaxis=dict(
                showgrid=True, 
                gridcolor="#111", 
                side="right", 
                range=[y_min - padding, y_max + padding],
                fixedrange=False
            ), 
            dragmode=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.markdown(f"""
    <style>
    @import url('https://fonts.cdnfonts.com/css/tinos');
    
    .stApp {{ background-color: #000000; font-family: 'Tinos', 'Inter', sans-serif; }}
    
    /* REGRAS DE VISIBILIDADE */
    .mobile-view {{ display: none; }}
    .desktop-view {{ display: block; }}

    .main-title {{ font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; color: #FFFFFF; margin: 0; line-height: 1; font-family: 'Tinos', sans-serif; }}
    .sub-title {{ font-size: 0.7rem; letter-spacing: 2px; color: #555; text-transform: uppercase; margin-top: 5px; font-family: 'Tinos', sans-serif; }}
    
    .ticker-link {{ color: #FFFFFF !important; font-weight: 600; text-decoration: none !important; }}
    .pos-val {{ color: #00FF00; }}
    .neg-val {{ color: #FF4B4B; }}
    .white-val {{ color: #FFFFFF !important; }}
    
    .list-container {{ width: 100%; border-collapse: collapse; margin-top: 1rem; font-family: 'Tinos', sans-serif; border: 1px solid #222; }}
    .list-header {{ background-color: #0A0A0A; color: #FFA500; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; }}
    .list-header th {{ padding: 12px 8px; text-align: left; font-weight: 700; border: 1px solid #222; color: #FFA500; }}
    .list-row td {{ padding: 10px 8px; color: white; font-size: 0.8rem; border: 1px solid #222; }}
    .list-row:hover {{ background-color: #0F0F0F; }}
    .sector-row {{ background-color: #111; color: #FFA500; font-weight: 700; font-size: 0.75rem; letter-spacing: 1px; }}
    .sector-row td {{ padding: 15px 8px; border: 1px solid #222; }}

    details {{ background-color: #000; border-bottom: 1px solid #222; margin-bottom: 0px; font-family: 'Inter', sans-serif; }}
    summary {{ list-style: none; padding: 12px 10px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background-color: #050505; }}
    summary:hover {{ background-color: #111; }}
    
    .mob-header-left {{ display: flex; align-items: center; }}
    .mob-header-right {{ display: flex; flex-direction: column; align-items: flex-end; }}
    .mob-ticker {{ font-weight: 800; color: #FFF; font-size: 0.8rem; letter-spacing: -0.2px; }}
    .mob-price {{ color: #DDD; font-size: 0.8rem; font-weight: 600; margin-bottom: 1px; }}
    .mob-today {{ font-weight: 700; font-size: 0.75rem; }}
    
    .mob-content {{ padding: 12px; background-color: #111; border-top: 1px solid #222; }}
    .mob-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px 8px; }}
    .mob-item {{ display: flex; flex-direction: column; }}
    .mob-label {{ color: #666; font-size: 0.6rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px; }}
    .mob-val {{ color: #FFF; font-size: 0.85rem; font-weight: 500; }}
    
    .mob-sector {{ background-color: #1a1a1a; color: #FFA500; padding: 10px 10px; font-weight: 700; font-size: 0.8rem; letter-spacing: 1px; border-bottom: 1px solid #333; margin-top: 10px; }}

    [data-testid="stBaseButton-pills"] {{ 
        background-color: transparent !important; 
        border: none !important; 
        color: #888 !important; 
        border-radius: 0px !important;
        font-family: 'Tinos', sans-serif !important;
        padding: 4px 12px !important;
    }}
    [data-testid="stBaseButton-pillsActive"] {{ 
        background-color: transparent !important; 
        color: #FFFFFF !important; 
        border: none !important; 
        border-bottom: 1px solid #FFFFFF !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
    }}

    @media (max-width: 768px) {{
        .mobile-view {{ display: block !important; }}
        .desktop-view {{ display: none !important; }}
        
        div[data-testid="stPills"] {{ display: block !important; }}
        div[data-testid="stPills"] > div {{ display: flex !important; flex-direction: column !important; width: 100% !important; }}
        div[data-testid="stPills"] button {{
            width: 100% !important;
            max-width: 100% !important;
            margin: 2px 0px !important;
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 1px solid #333 !important;
            border-radius: 0px !important;
            justify-content: flex-start !important;
            text-align: left !important;
            padding: 12px !important;
        }}
        div[data-testid="stPills"] button[aria-checked="true"] {{
            background-color: #111 !important;
            border: 1px solid #FFFFFF !important;
        }}

        div[data-testid="column"]:nth-child(2) {{ 
            margin-top: 15px !important; 
            width: 100% !important; 
            display: flex !important;
            justify-content: flex-end !important;
        }}
        
        div[data-testid="stPopoverBody"] > div {{
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            text-align: center !important;
        }}
    }}

    div.stButton > button {{ background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; }}
    
    div[data-testid="stPopover"] > button {{ 
        height: auto !important; 
        min-height: 0px !important; 
        padding: 4px 16px !important; 
        background-color: transparent !important; 
        color: #FFFFFF !important; 
        border: 1px solid #FFFFFF !important; 
        font-size: 0.8rem !important;
        font-weight: 400 !important;
        width: auto !important;
    }}
    div[data-testid="stPopoverBody"] {{ background-color: #0A0A0A !important; border: 1px solid #333 !important; }}

    header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.5rem !important; }}
    </style>
""", unsafe_allow_html=True)

# 2. DICIONÁRIOS MESTRE (Mantidos conforme sua instrução)
INDICES_LIST = ["^BVSP", "EWZ", "^GSPC", "^NDX", "^DJI", "^VIX", "^N225", "^HSI", "000001.SS", "^GDAXI", "^FTSE", "^FCHI", "^STOXX50E", "BRL=X", "DX-Y.NYB", "BTC-USD", "ES=F", "BZ=F", "TIO=F", "GC=F"]
COBERTURA = {
    "AZZA3.SA": {"Rec": "Compra", "Alvo": 50.00}, "LREN3.SA": {"Rec": "Compra", "Alvo": 23.00},
    "MGLU3.SA": {"Rec": "Neutro", "Alvo": 10.00}, "MELI": {"Rec": "Compra", "Alvo": 2810.00},
    "ASAI3.SA": {"Rec": "Compra", "Alvo": 18.00}, "RADL3.SA": {"Rec": "Compra", "Alvo": 29.00},
    "SMFT3.SA": {"Rec": "Compra", "Alvo": 36.00}, "NATU3.SA": {"Rec": "Compra", "Alvo": 15.00},
    "AUAU3.SA": {"Rec": "Neutro", "Alvo": 3.00}, "ABEV3.SA": {"Rec": "Neutro", "Alvo": 15.00},
    "MULT3.SA": {"Rec": "Compra", "Alvo": 35.00}, "WEGE3.SA": {"Rec": "Neutro", "Alvo": 49.00},
    "RENT3.SA": {"Rec": "Compra", "Alvo": 58.00}, "SLCE3.SA": {"Rec": "Compra", "Alvo": 24.60},
    "JBS": {"Rec": "Compra", "Alvo": 20.00}, "MBRF3.SA": {"Rec": "Neutro", "Alvo": 22.00},
    "BEEF3.SA": {"Rec": "Neutro", "Alvo": 7.00}, "EZTC3.SA": {"Rec": "Compra", "Alvo": 24.00},
    "MRVE3.SA": {"Rec": "Neutro", "Alvo": 9.50}
}
SETORES_ACOMPANHAMENTO = {
    "IBOV": ["^BVSP"],
    "Varejo e Bens de Consumo": ["AZZA3.SA", "LREN3.SA", "CEAB3.SA", "GUAR3.SA", "TFCO4.SA", "VIVA3.SA", "SBFG3.SA", "MELI", "MGLU3.SA", "BHIA3.SA", "ASAI3.SA", "GMAT3.SA", "PCAR3.SA", "SMFT3.SA", "NATU3.SA", "AUAU3.SA", "VULC3.SA", "ALPA4.SA"],
    "Farmácias e Farmacêuticas": ["RADL3.SA", "PGMN3.SA", "PNVL3.SA", "DMVF3.SA", "PFRM3.SA", "HYPE3.SA", "BLAU3.SA"],
    "Shoppings": ["MULT3.SA", "ALOS3.SA", "IGTI11.SA"],
    "Agronegócio e Proteínas": ["AGRO3.SA", "SLCE3.SA", "ABEV3.SA", "MDIA3.SA", "JBS", "MBRF3.SA", "BEEF3.SA", "SMTO3.SA", "KEPL3.SA"],
    "Bens de Capital": ["WEGE3.SA", "EMBJ3.SA", "LEVE3.SA", "TUPY3.SA", "MYPK3.SA", "FRAS3.SA", "RAPT4.SA", "POMO4.SA"],
    "Transporte e Logística": ["RENT3.SA", "MOVI3.SA", "VAMO3.SA", "RAIL3.SA", "SIMH3.SA"],
    "Bancos e Financeiras": ["ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "SANB11.SA", "NU", "BPAC11.SA", "XP", "INTR", "PAGS", "BRSR6.SA", "B3SA3.SA", "BBSE3.SA", "PSSA3.SA", "CXSE3.SA"],
    "Educação": ["YDUQ3.SA", "COGN3.SA", "ANIM3.SA", "SEER3.SA"],
    "Energia Elétrica": ["AXIA3.SA", "AURE3.SA", "EQTL3.SA", "EGIE3.SA", "TAEE11.SA", "ENEV3.SA", "CMIG4.SA", "CPLE3.SA", "CPFE3.SA", "ENGI11.SA", "ISA4.SA", "ALUP11.SA"],
    "Água e Saneamento": ["SBSP3.SA", "SAPR11.SA", "CSMG3.SA", "ORVR3.SA"],
    "Concessões": ["MOTV3.SA", "ECOR3.SA"],
    "Saúde": ["RDOR3.SA", "HAPV3.SA", "ODPV3.SA", "MATD3.SA", "FLRY3.SA"],
    "Tech e Telecom": ["VIVT3.SA", "TIMS3.SA", "TOTS3.SA", "LWSA3.SA"],
    "Construção e Real Estate": ["EZTC3.SA", "CYRE3.SA", "MRVE3.SA", "MDNE3.SA", "TEND3.SA", "MTRE3.SA", "PLPL3.SA", "DIRR3.SA", "CURY3.SA", "JHSF3.SA"],
    "Serviços": ["OPCT3.SA", "GGPS3.SA"],
    "Petróleo, Gás e Distribuição": ["PETR4.SA", "PRIO3.SA", "BRAV3.SA", "RECV3.SA", "CSAN3.SA", "VBBR3.SA", "UGPA3.SA"],
    "Mineração e Siderurgia": ["VALE3.SA", "CSNA3.SA", "USIM5.SA", "GGBR4.SA", "GOAU4.SA", "CMIN3.SA", "BRAP4.SA"],
    "Papel, Celulose e Químicos": ["SUZB3.SA", "KLBN11.SA", "RANI3.SA", "UNIP6.SA", "DEXP3.SA"]
}
CARTEIRA_PESSOAL_QTD = {
    "ITUB3.SA": 8, "WEGE3.SA": 5, "EGIE3.SA": 9, "EQTL3.SA": 9, "MULT3.SA": 7,
    "RENT3.SA": 3, "RADL3.SA": 5, "SMFT3.SA": 6, "MDIA3.SA": 5, "BBSE3.SA": 3,
    "LEVE3.SA": 5, "LREN3.SA": 3, "ASAI3.SA": 14, "BPAC3.SA": 2, "VIVT3.SA": 3,
    "UNIP3.SA": 2, "PRIO3.SA": 5, "VULC3.SA": 5, "PSSA3.SA": 5
}

# 3. FUNÇÕES
@st.cache_data(ttl=300)
def get_all_data(tickers):
    # threads=False resolve o conflito de RuntimeError no Streamlit
    return yf.download(tickers, period="6y", group_by='ticker', auto_adjust=True, progress=False, threads=False)

def calc_variation(h, days=None, ytd=False):
    try:
        cl = h['Close'].dropna()
        if cl.empty: return 0.0
        curr = float(cl.iloc[-1])
        if ytd:
            start_row = cl.loc[f"{datetime.now().year}-01-01":]
            start = float(start_row.iloc[0]) if not start_row.empty else float(cl.iloc[0])
        else:
            idx = -days if len(cl) >= days else 0
            if days == 1 and len(cl) > 1: idx = -2
            start = float(cl.iloc[idx])
        return ((curr / start) - 1) * 100
    except: return 0.0

def format_val_html(val, is_pct=False, sym="", force_white=False):
    if pd.isna(val) or val == 0: return "-"
    color_class = "white-val" if force_white else ("pos-val" if is_pct and val > 0 else ("neg-val" if is_pct and val < 0 else ""))
    f = "{:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")
    return f'<span class="{color_class}">{f + "%" if is_pct else sym + f}</span>'

# 4. INTERFACE
c1, c2 = st.columns([0.85, 0.15])
with c1:
    st.markdown(f'<div class="main-title">DASHBOARD</div><div class="sub-title">ÚLTIMA ATUALIZAÇÃO: {hora_atual}</div>', unsafe_allow_html=True)
with c2:
    if st.button("ATUALIZAR"):
        st.cache_data.clear()

all_tickers_master = sorted(list(set(list(COBERTURA.keys()) + [t for s in SETORES_ACOMPANHAMENTO.values() for t in s] + list(CARTEIRA_PESSOAL_QTD.keys()) + INDICES_LIST)))

# Tratamento para evitar que o erro de dados pare o app
try:
    master_data = get_all_data(all_tickers_master)
    if master_data.empty:
        st.error("Dados não disponíveis no momento.")
        st.stop()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

st.write("---")

opcoes_nav = ["Cobertura", "Acompanhamentos", "Carteira pessoal", "Índices"]
aba_selecionada = st.pills("", options=opcoes_nav, key="aba_ativa", label_visibility="collapsed")

cols_base = ["HOJE", "30D", "6M", "12M", "YTD", "5A"]
if aba_selecionada == "Cobertura":
    headers, t_list = ["Ticker", "Preço", "Rec.", "Alvo", "Upside"] + cols_base, sorted(list(COBERTURA.keys()))
elif aba_selecionada == "Carteira pessoal":
    headers = ["Ticker", "Preço", "Peso %"] + cols_base
    pesos_calc = [{"ticker": tk, "val": float(master_data[tk]['Close'].dropna().iloc[-1]) * CARTEIRA_PESSOAL_QTD[tk]} for tk in CARTEIRA_PESSOAL_QTD if tk in master_data]
    df_p = pd.DataFrame(pesos_calc)
    df_p["peso"] = (df_p["val"] / df_p["val"].sum()) * 100
    t_list = df_p.sort_values("peso", ascending=False)["ticker"].tolist()
elif aba_selecionada == "Índices":
    headers, t_list = ["Ticker", "Preço"] + cols_base, INDICES_LIST
else:
    headers, t_list = ["Ticker", "Preço"] + cols_base, []
    for s, ticks in SETORES_ACOMPANHAMENTO.items(): t_list.append({"setor": s}); t_list.extend(ticks)

tickers_da_aba = [tk for tk in t_list if not isinstance(tk, dict)]

with st.popover("GRÁFICOS", use_container_width=False):
    col_pop1, col_pop2 = st.columns(2)
    for i, tk in enumerate(tickers_da_aba):
        target_col = col_pop1 if i % 2 == 0 else col_pop2
        if target_col.button(tk, key=f"btn_{tk}", use_container_width=True):
            exibir_grafico_popup(tk, master_data)

# --- RENDERIZAÇÃO ---
html_desktop = f'<div class="desktop-view"><table class="list-container"><tr class="list-header">'
for h in headers: html_desktop += f'<th>{h}</th>'
html_desktop += '</tr>'

html_mobile = '<div class="mobile-view">'

for t in t_list:
    if isinstance(t, dict):
        sector_name = t["setor"].upper()
        html_desktop += f'<tr class="sector-row"><td colspan="{len(headers)}">{sector_name}</td></tr>'
        html_mobile += f'<div class="mob-sector">{sector_name}</div>'
        continue
    try:
        h = master_data[t]; cl = h['Close'].dropna(); p = float(cl.iloc[-1])
        sym = "R$ " if (t == "^BVSP" or ".SA" in t) else ("" if aba_selecionada == "Índices" else "US$ ")
        var_hoje = calc_variation(h, 1)
        html_desktop += f'<tr class="list-row"><td><span class="ticker-link">{t}</span></td><td>{format_val_html(p, sym=sym)}</td>'
        if aba_selecionada == "Cobertura":
            alv = COBERTURA[t]["Alvo"]; html_desktop += f'<td>{COBERTURA[t]["Rec"]}</td><td>{format_val_html(alv, sym=sym)}</td><td>{format_val_html((alv/p-1)*100, is_pct=True)}</td>'
        if aba_selecionada == "Carteira pessoal":
            peso_val = df_p[df_p["ticker"] == t]["peso"].values[0]; html_desktop += f'<td>{format_val_html(peso_val, is_pct=True, force_white=True)}</td>'
        for d in [1, 21, 126, 252]: html_desktop += f'<td>{format_val_html(calc_variation(h, d), is_pct=True)}</td>'
        html_desktop += f'<td>{format_val_html(calc_variation(h, ytd=True), is_pct=True)}</td><td>{format_val_html(calc_variation(h, 1260), is_pct=True)}</td></tr>'
        
        formatted_price = "{:,.2f}".format(p).replace(",", "X").replace(".", ",").replace("X", ".")
        html_mobile += f"""<details><summary><div class="mob-header-left"><span class="mob-ticker">{t}</span></div><div class="mob-header-right"><span class="mob-price">{sym}{formatted_price}</span><span class="mob-today">{format_val_html(var_hoje, is_pct=True)}</span></div></summary><div class="mob-content"><div class="mob-grid">"""
        if aba_selecionada == "Cobertura":
            alv = COBERTURA[t]["Alvo"]; html_mobile += f'<div class="mob-item"><span class="mob-label">REC</span><span class="mob-val">{COBERTURA[t]["Rec"]}</span></div><div class="mob-item"><span class="mob-label">ALVO</span><span class="mob-val">{format_val_html(alv, sym=sym)}</span></div><div class="mob-item"><span class="mob-label">UPSIDE</span><span class="mob-val">{format_val_html((alv/p-1)*100, is_pct=True)}</span></div>'
        if aba_selecionada == "Carteira pessoal":
            peso_val = df_p[df_p["ticker"] == t]["peso"].values[0]; html_mobile += f'<div class="mob-item"><span class="mob-label">PESO</span><span class="mob-val">{format_val_html(peso_val, is_pct=True, force_white=True)}</span></div>'
        html_mobile += f'<div class="mob-item"><span class="mob-label">30D</span><span class="mob-val">{format_val_html(calc_variation(h, 21), is_pct=True)}</span></div><div class="mob-item"><span class="mob-label">6M</span><span class="mob-val">{format_val_html(calc_variation(h, 126), is_pct=True)}</span></div><div class="mob-item"><span class="mob-label">12M</span><span class="mob-val">{format_val_html(calc_variation(h, 252), is_pct=True)}</span></div><div class="mob-item"><span class="mob-label">YTD</span><span class="mob-val">{format_val_html(calc_variation(h, ytd=True), is_pct=True)}</span></div><div class="mob-item"><span class="mob-label">5A</span><span class="mob-val">{format_val_html(calc_variation(h, 1260), is_pct=True)}</span></div>'
        html_mobile += """</div></div></details>"""
    except: continue

html_desktop += '</table></div>'
html_mobile += '</div>'
st.markdown(html_desktop + html_mobile, unsafe_allow_html=True)
