import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import numpy as np

# 1. CONFIGURAÇÃO E CSS
st.set_page_config(page_title="DASHBOARD", page_icon="favicon.png", layout="wide")

if "ticker_selecionado" not in st.session_state:
    st.session_state.ticker_selecionado = None
if "periodo_grafico" not in st.session_state:
    st.session_state.periodo_grafico = "12M"
if "aba_ativa" not in st.session_state:
    st.session_state.aba_ativa = "Cobertura"

hora_atual = datetime.now().strftime("%H:%M")

@st.dialog("Gráfico de Performance", width="large")
def exibir_grafico_popup(t_sel, data):
    per_map = {"30D": 21, "6M": 126, "12M": 252, "5A": 1260, "YTD": "ytd"}
    nova_selecao = st.pills("Periodo", options=list(per_map.keys()), key="pills_popup", default=st.session_state.periodo_grafico)
    if nova_selecao:
        st.session_state.periodo_grafico = nova_selecao
    
    try:
        h_raw = data[t_sel]['Close'].dropna()
    except:
        st.error("Dados insuficientes para gerar o gráfico.")
        return

    p_sel = st.session_state.periodo_grafico
    days = per_map.get(p_sel, 252)
    
    if days == "ytd":
        df_plot = h_raw.loc[f"{datetime.now().year}-01-01":]
    else:
        df_plot = h_raw.iloc[-days:] if len(h_raw) >= days else h_raw
    
    if not df_plot.empty:
        perf = ((df_plot.iloc[-1] / df_plot.iloc[0]) - 1) * 100
        color = "#00FF00" if perf >= 0 else "#FF4B4B"
        
        y_min, y_max = df_plot.min(), df_plot.max()
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
            template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
            height=400, margin=dict(l=0, r=0, t=10, b=0), 
            xaxis=dict(showgrid=False, fixedrange=True), 
            yaxis=dict(showgrid=True, gridcolor="#111", side="right", range=[y_min - padding, y_max + padding], fixedrange=True), 
            dragmode=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.markdown(f"""
    <style>
    @import url('https://fonts.cdnfonts.com/css/tinos');
    .stApp {{ background-color: #000000; font-family: 'Tinos', 'Inter', sans-serif; }}
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
    
    /* Estilo Rentabilidade Mensal e Anual */
    .rent-table {{ width: 100%; border-collapse: collapse; font-family: 'Tinos', sans-serif; font-size: 0.8rem; text-align: center; border: 1px solid #222; margin-top: 20px; }}
    .rent-table th {{ background-color: #0A0A0A; color: #FFA500; padding: 10px 5px; border: 1px solid #222; text-transform: uppercase; font-size: 0.7rem; }}
    .rent-table td {{ padding: 10px 5px; border: 1px solid #222; color: #FFF; }}
    .rent-year {{ background-color: #0A0A0A; font-weight: 700; color: #FFF !important; text-align: left; padding-left: 10px; }}
    .rent-total {{ background-color: #0A0A0A; font-weight: 700; }}

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
    [data-testid="stBaseButton-pills"] {{ background-color: transparent !important; border: none !important; color: #888 !important; border-radius: 0px !important; font-family: 'Tinos', sans-serif !important; padding: 4px 12px !important; }}
    [data-testid="stBaseButton-pillsActive"] {{ background-color: transparent !important; color: #FFFFFF !important; border: none !important; border-bottom: 1px solid #FFFFFF !important; border-radius: 0px !important; font-weight: 700 !important; }}
    @media (max-width: 768px) {{
        .mobile-view {{ display: block !important; }}
        .desktop-view {{ display: none !important; }}
        div[data-testid="stPills"] {{ display: block !important; }}
        div[data-testid="stPills"] > div {{ display: flex !important; flex-direction: column !important; width: 100% !important; }}
        div[data-testid="stPills"] button {{ width: 100% !important; max-width: 100% !important; margin: 2px 0px !important; background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #333 !important; border-radius: 0px !important; justify-content: flex-start !important; text-align: left !important; padding: 12px !important; }}
        div[data-testid="stPills"] button[aria-checked="true"] {{ background-color: #111 !important; border: 1px solid #FFFFFF !important; }}
        div[data-testid="column"]:nth-child(2) {{ margin-top: 15px !important; width: 100% !important; display: flex !important; justify-content: flex-end !important; }}
        div[data-testid="stPopoverBody"] > div {{ display: flex !important; flex-direction: column !important; align-items: center !important; text-align: center !important; }}
    }}
    div.stButton > button {{ background-color: #000000 !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; }}
    div[data-testid="stPopover"] > button {{ height: auto !important; min-height: 0px !important; padding: 4px 16px !important; background-color: transparent !important; color: #FFFFFF !important; border: 1px solid #FFFFFF !important; font-size: 0.8rem !important; font-weight: 400 !important; width: auto !important; }}
    div[data-testid="stPopoverBody"] {{ background-color: #0A0A0A !important; border: 1px solid #333 !important; }}
    header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.5rem !important; }}
    
    [data-testid="stStatusWidget"] {{ visibility: hidden !important; }}
    </style>
""", unsafe_allow_html=True)

# 2. DICIONÁRIOS MESTRE

# ==============================================================================
# EDITAR AQUI SEUS APORTES (TICKER, DATA da COMPRA no formato AAAA-MM-DD, QTD)
# ==============================================================================
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

    {"ticker": "VALE3.SA", "data": "2026-02-23", "qtd": 3},
    # Adicione novos aportes abaixo copiando a estrutura acima
]

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

# --- DICIONÁRIO BANCO DE DADOS MACRO (BCB + IPEADATA) ---
DB_MACRO = {
    # === BCB ===
    "Índice de confiança de serviços": {"fonte": "bcb", "codigo": 17660, "freq": "mensal"},
    "CDI anualizado": {"fonte": "bcb", "codigo": 4389, "freq": "diario"},
    "TJLP mensal": {"fonte": "bcb", "codigo": 256, "freq": "mensal"},
    "Taxa Selic": {"fonte": "bcb", "codigo": 432, "freq": "diario"},
    "PIB mensal - R$ MM": {"fonte": "bcb", "codigo": 4380, "freq": "mensal"},
    "PIB acum. Ano - R$ MM": {"fonte": "bcb", "codigo": 4381, "freq": "mensal"},
    "PIB acum. 12m - R$ MM": {"fonte": "bcb", "codigo": 4382, "freq": "mensal"},
    "PIB anual - R$ MM": {"fonte": "bcb", "codigo": 1208, "freq": "anual"},
    "Meta inflação": {"fonte": "bcb", "codigo": 13521, "freq": "anual"},
    "IGP-M - Mensal": {"fonte": "bcb", "codigo": 189, "freq": "mensal"},
    "IGP-DI - Mensal": {"fonte": "bcb", "codigo": 190, "freq": "mensal"},
    "IPCA - Mensal": {"fonte": "bcb", "codigo": 433, "freq": "mensal"},
    "IPCA alimentos e bebidas - Mensal": {"fonte": "bcb", "codigo": 1635, "freq": "mensal"},
    "IPCA vestuário - Mensal": {"fonte": "bcb", "codigo": 1638, "freq": "mensal"},
    "IPCA geral acum. 12m": {"fonte": "bcb", "codigo": 13522, "freq": "mensal"},
    # === IPEADATA ===
    "Intenção de consumo das famílias ajustado (ICF)": {"fonte": "ipea", "codigo": "CNC12_ICFAJ12", "freq": "mensal"},
    "Famílias endividadas total": {"fonte": "ipea", "codigo": "CNC12_PEICT12", "freq": "mensal"},
    "Taxa de desemprego": {"fonte": "ipea", "codigo": "PNADC12_TDESOC12", "freq": "mensal"},
    "Massa salarial real": {"fonte": "ipea", "codigo": "PNADC12_MRRTH12", "freq": "mensal"},
    "Renda real habitual": {"fonte": "ipea", "codigo": "PNADC12_RRTH12", "freq": "mensal"},
    "Produção industrial - Bebidas": {"fonte": "ipea", "codigo": "PIMPFN12_QIIGNN212", "freq": "mensal"},
    "Volume de vendas no varejo - Geral": {"fonte": "ipea", "codigo": "PMC12_IVVRN12", "freq": "mensal"},
    "Volume de vendas no varejo - Artigos farmacêuticos": {"fonte": "ipea", "codigo": "PMC12_VRFARMN12", "freq": "mensal"},
    "Volume de vendas no varejo - Hipermercados e supermercados": {"fonte": "ipea", "codigo": "PMC12_VRSUPTN12", "freq": "mensal"},
    "Volume de vendas no varejo - Tecidos, vestuário e calçados": {"fonte": "ipea", "codigo": "PMC12_VRVESTN12", "freq": "mensal"},
    "População no Brasil (projeção)": {"fonte": "ipea", "codigo": "DEPIS_POPP", "freq": "anual"},
    "População no Brasil (estimativa)": {"fonte": "ipea", "codigo": "DEPIS_POP", "freq": "anual"},
    "Salário mínimo vigente": {"fonte": "ipea", "codigo": "MTE12_SALMIN12", "freq": "mensal"},
    "Salário mínimo real": {"fonte": "ipea", "codigo": "GAC12_SALMINRE12", "freq": "mensal"},
    "Concessões de crédito PF": {"fonte": "ipea", "codigo": "BM12_CCAPF12", "freq": "mensal"},
    "Concessões de crédito PJ": {"fonte": "ipea", "codigo": "BM12_CCAPJ12", "freq": "mensal"},
    "Taxa média de juros PF": {"fonte": "ipea", "codigo": "BM12_CTJPF12", "freq": "mensal"},
    "Saldo de crédito PF recursos livres": {"fonte": "ipea", "codigo": "BM12_CRLSPF12", "freq": "mensal"}
}

# 3. FUNÇÕES
@st.cache_data(ttl=300)
def get_all_data(tickers):
    try:
        with st.spinner(""):
            data = yf.download(tickers, period="5y", group_by='ticker', auto_adjust=True, progress=False, threads=True)
        return data if not data.empty else pd.DataFrame()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600) # Cache longo para dados macro
def get_macro_data(item_name, item_info, start_date=None, end_date=None):
    """
    Busca dados macroeconômicos sob demanda e aplica limpeza universal.
    Suporta: BCB (SGS) e IPEADATA (API).
    """
    df_final = pd.DataFrame()
    try:
        # ================== LÓGICA BCB ==================
        if item_info["fonte"] == "bcb":
            code = item_info["codigo"]
            url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json"
            
            # Tratamento de limite de 10 anos para diários
            if start_date:
                url += f"&dataInicial={start_date.strftime('%d/%m/%Y')}"
            if end_date:
                url += f"&dataFinal={end_date.strftime('%d/%m/%Y')}"
            
            df = pd.read_json(url)
            
            # Tratamento de valores BCB
            if 'valor' in df.columns:
                df['valor'] = df['valor'].astype(str)
                df['valor'] = df['valor'].str.replace(',', '.', regex=False)
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
                df = df.dropna(subset=['valor'])
            
            df['data'] = pd.to_datetime(df['data'], dayfirst=True)

        # ================== LÓGICA IPEADATA ==================
        elif item_info["fonte"] == "ipea":
            code = item_info["codigo"]
            # Endpoint API OData v4 do Ipea
            url = f"https://www.ipeadata.gov.br/api/odata4/Metadados('{code}')/Valores"
            
            df_raw = pd.read_json(url)
            
            # Ipeadata retorna lista dentro da chave 'value'
            if 'value' in df_raw.columns:
                df = pd.DataFrame(df_raw['value'].tolist())
                # Padronizar nomes de coluna
                if 'VALDATA' in df.columns and 'VALVALOR' in df.columns:
                    df = df.rename(columns={'VALDATA': 'data', 'VALVALOR': 'valor'})
                    
                    # CORREÇÃO ROBUSTA: Garantir conversão para datetime antes de usar .dt
                    # utc=True unifica o formato, errors='coerce' evita falha total
                    df['data'] = pd.to_datetime(df['data'], errors='coerce', utc=True)
                    df = df.dropna(subset=['data'])
                    
                    # Agora é seguro remover o timezone
                    df['data'] = df['data'].dt.tz_localize(None)
                else:
                    return pd.DataFrame()
            else:
                return pd.DataFrame()
        
        # ================== FILTROS E FORMATACAO COMUM ==================
        if not df.empty:
            # Filtro de Datas (Universal)
            if start_date:
                df = df[df['data'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['data'] <= pd.to_datetime(end_date)]
                
            freq = item_info.get("freq", "diario")
            
            if freq == "mensal":
                meses_map = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 
                             7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}
                df['Data'] = df['data'].apply(lambda x: f"{meses_map[x.month]}/{str(x.year)[2:]}")
            elif freq == "anual":
                df['Data'] = df['data'].dt.year.astype(str)
            else: # diario
                df['Data'] = df['data'].dt.strftime('%d/%m/%Y')
            
            df_final = df[['Data', 'valor']].rename(columns={'valor': 'Valor'})
            
    except Exception as e:
        st.error(f"Erro ao buscar dados de {item_name}: {e}")
        
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
c1, c2 = st.columns([0.92, 0.08]) 
with c1:
    st.markdown(f'<div class="main-title">DASHBOARD</div><div class="sub-title">ÚLTIMA ATUALIZAÇÃO: {hora_atual}</div>', unsafe_allow_html=True)
with c2:
    if st.button("ATUALIZAR"):
        st.cache_data.clear()
        st.rerun()

# Lista de tickers para download (inclui cobertura, setores, carteira e indices)
# Extrai tickers únicos da lista de aportes
tickers_carteira_usuario = list(set([item['ticker'] for item in APORTES_USUARIO]))
all_tickers_master = sorted(list(set(list(COBERTURA.keys()) + [t for s in SETORES_ACOMPANHAMENTO.values() for t in s] + tickers_carteira_usuario + INDICES_LIST)))
master_data = get_all_data(all_tickers_master)

if master_data.empty:
    st.error("Dados não disponíveis no momento.")
    st.stop()

st.write("---")

opcoes_nav = ["Cobertura", "Acompanhamentos", "Carteira pessoal", "Índices", "Backtest", "Banco de dados", "Calendário econômico"]
aba_selecionada = st.pills("", options=opcoes_nav, key="aba_ativa", label_visibility="collapsed")

if aba_selecionada == "Banco de dados":
    c_sel, c_d1, c_d2 = st.columns([2, 1, 1])
    with c_sel:
        # Alterado para index=None e placeholder
        indicador = st.selectbox("Indicador Econômico", options=sorted(list(DB_MACRO.keys())), index=None, placeholder="Selecionar indicador")
    with c_d1:
        d_ini = st.date_input("Data Início", value=datetime(2020, 1, 1))
    with c_d2:
        d_fim = st.date_input("Data Fim", value=datetime.now())
    
    if indicador:
        info = DB_MACRO[indicador]
        df_macro = get_macro_data(indicador, info, start_date=d_ini, end_date=d_fim)
        
        if not df_macro.empty:
            st.markdown(f"#### {indicador}")
            
            # Converter para CSV para download
            csv = df_macro.to_csv(index=False).encode('utf-8')
            
            c_down, c_view = st.columns([1, 4])
            with c_down:
                st.download_button(
                    label="Baixar CSV",
                    data=csv,
                    file_name=f"{indicador.replace(' ', '_').lower()}.csv",
                    mime='text/csv',
                )
            
            # Exibição simples da tabela
            st.dataframe(
                df_macro, 
                hide_index=True, 
                use_container_width=False, 
                width=400,
                column_config={
                    "Valor": st.column_config.NumberColumn(format="%.2f")
                }
            )

            # --- GRÁFICO ---
            fig_macro = go.Figure()
            fig_macro.add_trace(go.Scatter(
                x=df_macro['Data'],
                y=df_macro['Valor'],
                mode='lines',
                line=dict(color='#FF9900', width=2),
                name=indicador
            ))
            fig_macro.update_layout(
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=20, b=0),
                height=300,
                showlegend=False,
                xaxis=dict(showgrid=False, fixedrange=True),
                yaxis=dict(showgrid=True, gridcolor="#222", fixedrange=True),
                dragmode=False # Permite scroll no mobile
            )
            st.plotly_chart(fig_macro, use_container_width=True, config={'displayModeBar': False})
            # -------------------------------

        else:
            st.warning("Não foi possível carregar os dados para este indicador.")
    st.stop()

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
    
    if st.button("Gerar Backtest"):
        if ticker_raw:
            ticker_bt = f"{ticker_raw}.SA" if (len(ticker_raw) >= 5 and "." not in ticker_raw) else ticker_raw
            
            try:
                bt_data = yf.download([ticker_bt, benchmark], start=data_ini, end=data_fim, auto_adjust=True)['Close']
                if not bt_data.empty:
                    # 1. Gráfico de Performance (Base 100)
                    df_norm = (bt_data / bt_data.iloc[0]) * 100
                    
                    var_ticker = ((bt_data[ticker_bt].iloc[-1] / bt_data[ticker_bt].iloc[0]) - 1) * 100
                    var_bench = ((bt_data[benchmark].iloc[-1] / bt_data[benchmark].iloc[0]) - 1) * 100
                    
                    fig_bt = go.Figure()
                    
                    fig_bt.add_trace(go.Scatter(
                        x=df_norm.index, 
                        y=df_norm[ticker_bt], 
                        name=f"{ticker_bt} ({var_ticker:+.2f}%)", 
                        line=dict(color="#FFFFFF", width=2)
                    ))
                    
                    fig_bt.add_trace(go.Scatter(
                        x=df_norm.index, 
                        y=df_norm[benchmark], 
                        name=f"{bench_label} ({var_bench:+.2f}%)", 
                        line=dict(color="#FF9900", width=1.5)
                    ))
                    
                    fig_bt.update_layout(
                        title=dict(text="Performance Base 100", font=dict(color="#FFF", size=14), yanchor="top", y=1),
                        template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        height=450, margin=dict(l=0, r=0, t=40, b=0), 
                        xaxis=dict(showgrid=False, fixedrange=True),
                        yaxis=dict(showgrid=True, gridcolor="#222", side="right", fixedrange=True),
                        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
                        dragmode=False # Permite scroll no mobile
                    )
                    st.plotly_chart(fig_bt, use_container_width=True, config={'displayModeBar': False})

                    # 2. Gráfico de Volatilidade Anualizada (Janela 21 dias)
                    returns = bt_data.pct_change()
                    vol_ticker = returns[ticker_bt].rolling(window=21).std() * (252 ** 0.5) * 100
                    vol_bench = returns[benchmark].rolling(window=21).std() * (252 ** 0.5) * 100
                    
                    vol_ticker = vol_ticker.dropna()
                    vol_bench = vol_bench.dropna()
                    
                    fig_vol = go.Figure()
                    
                    fig_vol.add_trace(go.Scatter(
                        x=vol_ticker.index, 
                        y=vol_ticker, 
                        name=f"Vol. {ticker_bt}", 
                        line=dict(color="#FFFFFF", width=1.5)
                    ))
                    
                    fig_vol.add_trace(go.Scatter(
                        x=vol_bench.index, 
                        y=vol_bench, 
                        name=f"Vol. {bench_label}", 
                        line=dict(color="#FF9900", width=1.5)
                    ))
                    
                    fig_vol.update_layout(
                        title=dict(text="Volatilidade Anualizada (21 dias úteis)", font=dict(color="#FFF", size=14), yanchor="top", y=1),
                        template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        height=350, margin=dict(l=0, r=0, t=40, b=0), 
                        xaxis=dict(showgrid=False, fixedrange=True),
                        yaxis=dict(showgrid=True, gridcolor="#222", side="right", title="%", fixedrange=True),
                        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
                        dragmode=False # Permite scroll no mobile
                    )
                    st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})

                    # 3. Gráfico de Drawdown
                    dd_ticker = (bt_data[ticker_bt] / bt_data[ticker_bt].cummax() - 1) * 100
                    dd_bench = (bt_data[benchmark] / bt_data[benchmark].cummax() - 1) * 100

                    fig_dd = go.Figure()

                    fig_dd.add_trace(go.Scatter(
                        x=dd_ticker.index,
                        y=dd_ticker,
                        name=f"DD {ticker_bt}",
                        line=dict(color="#FFFFFF", width=1),
                        fill='tozeroy',
                        fillcolor='rgba(255, 255, 255, 0.1)'
                    ))

                    fig_dd.add_trace(go.Scatter(
                        x=dd_bench.index,
                        y=dd_bench,
                        name=f"DD {bench_label}",
                        line=dict(color="#FF9900", width=1),
                        fill='tozeroy',
                        fillcolor='rgba(255, 153, 0, 0.1)'
                    ))

                    fig_dd.update_layout(
                        title=dict(text="Drawdown (%)", font=dict(color="#FFF", size=14), yanchor="top", y=1),
                        template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        height=350, margin=dict(l=0, r=0, t=40, b=0),
                        xaxis=dict(showgrid=False, fixedrange=True),
                        yaxis=dict(showgrid=True, gridcolor="#222", side="right", fixedrange=True),
                        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
                        dragmode=False # Permite scroll no mobile
                    )
                    st.plotly_chart(fig_dd, use_container_width=True, config={'displayModeBar': False})

                    # 4. TABELA DE RENTABILIDADE MENSAL
                    st.markdown(f"<div style='color:#FFF; font-size:14px; font-weight:700; margin-top:30px; margin-bottom:10px;'>Rentabilidade Mensal - {ticker_bt}</div>", unsafe_allow_html=True)
                    
                    monthly_prices = bt_data[ticker_bt].resample('ME').last()
                    first_price = bt_data[ticker_bt].iloc[0]
                    m_ret = monthly_prices.pct_change() * 100
                    
                    if not m_ret.empty:
                        m_ret.iloc[0] = ((monthly_prices.iloc[0] / first_price) - 1) * 100

                    df_m = m_ret.to_frame()
                    df_m['ano'] = df_m.index.year
                    df_m['mes'] = df_m.index.month
                    
                    month_names = {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN', 7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}
                    pivot_ret = df_m.pivot(index='ano', columns='mes', values=ticker_bt)
                    pivot_ret = pivot_ret.rename(columns=month_names)
                    
                    cols_ordered = [month_names[i] for i in range(1, 13) if month_names[i] in pivot_ret.columns]
                    pivot_ret = pivot_ret[cols_ordered]

                    for year in pivot_ret.index:
                        y_data = bt_data[ticker_bt][bt_data[ticker_bt].index.year == year]
                        y_val = ((y_data.iloc[-1] / y_data.iloc[0]) - 1) * 100
                        pivot_ret.loc[year, 'ANO'] = y_val

                    html_rent = ['<table class="rent-table"><tr><th>ANO</th>']
                    for m in pivot_ret.columns: html_rent.append(f'<th>{m}</th>')
                    html_rent.append('</tr>')
                    
                    for year in pivot_ret.index[::-1]: 
                        html_rent.append(f'<tr><td class="rent-year">{year}</td>')
                        for col in pivot_ret.columns:
                            val = pivot_ret.loc[year, col]
                            if pd.isna(val):
                                html_rent.append('<td>-</td>')
                            else:
                                color = "#00FF00" if val > 0 else ("#FF4B4B" if val < 0 else "#FFF")
                                css_class = "rent-total" if col == "ANO" else ""
                                html_rent.append(f'<td class="{css_class}" style="color:{color}">{val:.2f}%</td>')
                        html_rent.append('</tr>')
                    html_rent.append('</table>')
                    st.markdown("".join(html_rent), unsafe_allow_html=True)

                    # 5. TABELA DE RENTABILIDADE ANUAL VS BENCHMARK
                    st.markdown(f"<div style='color:#FFF; font-size:14px; font-weight:700; margin-top:30px; margin-bottom:10px;'>Rentabilidade Anual - {ticker_bt}</div>", unsafe_allow_html=True)
                    
                    annual_comparison = []
                    years_list = sorted(bt_data.index.year.unique(), reverse=True)
                    
                    for yr in years_list:
                        yr_prices = bt_data[bt_data.index.year == yr]
                        t_ret_yr = ((yr_prices[ticker_bt].iloc[-1] / yr_prices[ticker_bt].iloc[0]) - 1) * 100
                        b_ret_yr = ((yr_prices[benchmark].iloc[-1] / yr_prices[benchmark].iloc[0]) - 1) * 100
                        rel_yr = t_ret_yr - b_ret_yr
                        annual_comparison.append({"ano": yr, "ticker": t_ret_yr, "bench": b_ret_yr, "rel": rel_yr})
                    
                    html_annual = ['<table class="rent-table"><tr><th>ANO</th>', f'<th>{ticker_bt}</th>', f'<th>{bench_label}</th>', '<th>RELATIVO</th></tr>']
                    for row in annual_comparison:
                        c_t = "#00FF00" if row["ticker"] > 0 else ("#FF4B4B" if row["ticker"] < 0 else "#FFF")
                        c_b = "#00FF00" if row["bench"] > 0 else ("#FF4B4B" if row["bench"] < 0 else "#FFF")
                        c_r = "#00FF00" if row["rel"] > 0 else ("#FF4B4B" if row["rel"] < 0 else "#FFF")
                        
                        html_annual.append(f'<tr><td class="rent-year">{row["ano"]}</td>')
                        html_annual.append(f'<td style="color:{c_t}">{row["ticker"]:.2f}%</td>')
                        html_annual.append(f'<td style="color:{c_b}">{row["bench"]:.2f}%</td>')
                        html_annual.append(f'<td class="rent-total" style="color:{c_r}">{row["rel"]:.2f}%</td></tr>')
                    html_annual.append('</table><br>')
                    st.markdown("".join(html_annual), unsafe_allow_html=True)

                else:
                    st.warning("Nenhum dado encontrado para os parâmetros selecionados.")
            except Exception as e:
                st.error(f"Erro ao processar backtest: {e}")
        else:
            st.error("Por favor, digite um ticker.")
    st.stop()

if aba_selecionada == "Calendário econômico":
    html_calendar = """
    <iframe src="https://sslecal2.investing.com?ecoDayBackground=%23000000&defaultFont=%23000000&innerBorderColor=%23ffffff&borderColor=%23ffffff&ecoDayFontColor=%23ffffff&columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&features=datepicker,timeselector,filters&countries=17,32,37,5,35,4,72&calType=day&timeZone=12&lang=12" width="100%" height="650" frameborder="0" allowtransparency="true" marginwidth="0" marginheight="0"></iframe>
    <div class="poweredBy" style="font-family: Arial, Helvetica, sans-serif;">
        <span style="font-size: 11px;color: #333333;text-decoration: none;">Calendário Econômico fornecido por <a href="https://br.investing.com/" rel="nofollow" target="_blank" style="font-size: 11px;color: #06529D; font-weight: bold;" class="underline_link">Investing.com Brasil</a>, o portal líder financeiro.</span>
    </div>
    """
    components.html(html_calendar, height=700, scrolling=True)
    st.stop()

cols_base = ["HOJE", "30D", "6M", "12M", "YTD", "5A"]
df_p = pd.DataFrame()

if aba_selecionada == "Cobertura":
    headers, t_list = ["Ticker", "Preço", "Rec.", "Alvo", "Upside"] + cols_base, sorted(list(COBERTURA.keys()))
elif aba_selecionada == "Carteira pessoal":
    if not APORTES_USUARIO:
        st.info("Adicione ativos na lista 'APORTES_USUARIO' no código para ver sua carteira.")
        st.stop()

    # Processar Aportes
    df_aportes = pd.DataFrame(APORTES_USUARIO)
    df_aportes['data'] = pd.to_datetime(df_aportes['data'])
    start_date = df_aportes['data'].min()
    
    # Lista de ativos da carteira + Ibovespa
    tickers_carteira = df_aportes['ticker'].unique().tolist()
    if "^BVSP" not in tickers_carteira: tickers_carteira.append("^BVSP")
    
    # Garantir que temos dados no master_data suficientes
    try:
        valid_tickers = [t for t in tickers_carteira if t in master_data.columns.levels[0]]
        prices = pd.DataFrame({t: master_data[t]['Close'] for t in valid_tickers})
        
        # Ajuste de timezone e filtro de data
        prices.index = prices.index.tz_localize(None)
        prices = prices.sort_index().loc[start_date:]
        prices = prices.fillna(method='ffill')
    except Exception as e:
        st.error(f"Erro ao processar dados históricos da carteira: {e}")
        st.stop()

    # Construir DataFrame de Quantidades Diárias (Holdings)
    all_dates = prices.index
    df_qtd = pd.DataFrame(0, index=all_dates, columns=[t for t in tickers_carteira if t != "^BVSP"])
    
    for _, row in df_aportes.iterrows():
        idx_loc = df_qtd.index.searchsorted(row['data'])
        if idx_loc < len(df_qtd):
            df_qtd.iloc[idx_loc:, df_qtd.columns.get_loc(row['ticker'])] += row['qtd']

    # --- CÁLCULO DE RENTABILIDADE (SISTEMA DE COTAS) ---
    cols_ativos = [t for t in tickers_carteira if t != "^BVSP" and t in prices.columns]
    pct_change = prices[cols_ativos].pct_change().fillna(0)
    
    # Alinha df_qtd com prices (garante mesmas colunas e indices)
    df_qtd_aligned = df_qtd[cols_ativos].reindex(prices.index).fillna(method='ffill').fillna(0)
    
    pos_yesterday = (prices[cols_ativos].shift(1) * df_qtd_aligned.shift(1)).fillna(0)
    total_yesterday = pos_yesterday.sum(axis=1)
    
    weights = pos_yesterday.div(total_yesterday, axis=0).fillna(0)
    portfolio_ret = (weights * pct_change).sum(axis=1)
    
    # Índice Base 100
    portfolio_idx = (1 + portfolio_ret).cumprod() * 100
    if "^BVSP" in prices.columns:
        ibov_idx = (1 + prices["^BVSP"].pct_change().fillna(0)).cumprod() * 100
    else:
        ibov_idx = pd.Series(100, index=portfolio_idx.index)
    
    # Normalizar
    if len(portfolio_idx) > 0:
        portfolio_idx = (portfolio_idx / portfolio_idx.iloc[0]) * 100
        ibov_idx = (ibov_idx / ibov_idx.iloc[0]) * 100

    # --- TABELA DE POSIÇÃO NO TOPO (SEM QTD) ---
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
            v_h = calc_variation(cl, 1)
            v_30 = calc_variation(cl, 21)
            v_6m = calc_variation(cl, 126)
            v_12 = calc_variation(cl, 252)
            v_ytd = calc_variation(cl, ytd=True)
            v_5a = calc_variation(cl, 1260)
            
            pos_data.append({
                "Ticker": t, "Preço": p, "Total": val,
                "HOJE": v_h, "30D": v_30, "6M": v_6m, 
                "12M": v_12, "YTD": v_ytd, "5A": v_5a
            })
            total_portfolio_val += val
        except: continue
    
    df_pos_table = pd.DataFrame(pos_data)
    
    if not df_pos_table.empty:
        df_pos_table["Peso %"] = (df_pos_table["Total"] / total_portfolio_val) * 100
        df_pos_table = df_pos_table.sort_values("Peso %", ascending=False)
        
        # Render HTML Table
        html_cart = [f'<div class="desktop-view"><table class="list-container"><tr class="list-header"><th>Ticker</th><th>Preço</th><th>Total</th><th>Peso %</th><th>HOJE</th><th>30D</th><th>6M</th><th>12M</th><th>YTD</th><th>5A</th></tr>']
        html_mob_cart = ['<div class="mobile-view">']

        for _, row in df_pos_table.iterrows():
            sym = "R$ "
            t = row["Ticker"]
            p = row["Preço"]
            
            html_cart.append(f'<tr class="list-row"><td><span class="ticker-link">{t}</span></td><td>{format_val_html(p, sym=sym)}</td><td>{format_val_html(row["Total"], sym=sym)}</td><td>{format_val_html(row["Peso %"], is_pct=True, force_white=True)}</td>')
            for col in ["HOJE", "30D", "6M", "12M", "YTD", "5A"]:
                html_cart.append(f'<td>{format_val_html(row[col], is_pct=True)}</td>')
            html_cart.append('</tr>')

            # Mobile
            f_p = "{:,.2f}".format(p).replace(",", "X").replace(".", ",").replace("X", ".")
            html_mob_cart.append(f'<details><summary><div class="mob-header-left"><span class="mob-ticker">{t}</span></div><div class="mob-header-right"><span class="mob-price">{sym}{f_p}</span><span class="mob-today">{format_val_html(row["HOJE"], is_pct=True)}</span></div></summary><div class="mob-content"><div class="mob-grid">')
            html_mob_cart.append(f'<div class="mob-item"><span class="mob-label">TOTAL</span><span class="mob-val">{format_val_html(row["Total"], sym=sym)}</span></div>')
            html_mob_cart.append(f'<div class="mob-item"><span class="mob-label">PESO</span><span class="mob-val">{format_val_html(row["Peso %"], is_pct=True, force_white=True)}</span></div>')
            for col in ["30D", "6M", "12M", "YTD", "5A"]:
                html_mob_cart.append(f'<div class="mob-item"><span class="mob-label">{col}</span><span class="mob-val">{format_val_html(row[col], is_pct=True)}</span></div>')
            html_mob_cart.append('</div></div></details>')

        html_cart.append('</table></div>')
        html_mob_cart.append('</div>')
        st.markdown("".join(html_cart) + "".join(html_mob_cart), unsafe_allow_html=True)

    # --- GRÁFICOS ---
    c_chart1, c_chart2 = st.columns(2)
    
    var_cart = (portfolio_idx.iloc[-1] - 100)
    var_ibov = (ibov_idx.iloc[-1] - 100)
    
    # 1. Performance vs Ibov
    with c_chart1:
        fig_perf = go.Figure()
        fig_perf.add_trace(go.Scatter(x=portfolio_idx.index, y=portfolio_idx, name=f"Carteira ({var_cart:+.2f}%)", line=dict(color="#FFFFFF", width=2)))
        fig_perf.add_trace(go.Scatter(x=ibov_idx.index, y=ibov_idx, name=f"Ibovespa ({var_ibov:+.2f}%)", line=dict(color="#FF9900", width=2)))
        
        fig_perf.update_layout(
            title=dict(text='Rentabilidade vs Ibovespa', x=0, font=dict(size=14, color='white'), y=1),
            template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=350,
            xaxis=dict(showgrid=False, fixedrange=True), 
            yaxis=dict(showgrid=True, gridcolor="#333", side="right", fixedrange=True), 
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0),
            dragmode=False, margin=dict(l=0, r=0, t=40, b=40)
        )
        st.plotly_chart(fig_perf, use_container_width=True, config={'displayModeBar': False})

    # 2. Evolução Patrimônio (Barras)
    with c_chart2:
        net_worth_series = (df_qtd_aligned * prices[cols_ativos]).sum(axis=1)
        fig_nw = go.Figure()
        fig_nw.add_trace(go.Bar(x=net_worth_series.index, y=net_worth_series, name="Patrimônio", marker_color="#FF9900"))
        
        fig_nw.update_layout(
            title=dict(text='Evolução do Patrimônio', x=0, font=dict(size=14, color='white'), y=1),
            template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=350,
            xaxis=dict(showgrid=False, fixedrange=True),
            yaxis=dict(showgrid=True, gridcolor="#333", side="right", fixedrange=True),
            showlegend=False, dragmode=False, margin=dict(l=0, r=0, t=40, b=40)
        )
        st.plotly_chart(fig_nw, use_container_width=True, config={'displayModeBar': False})

    # 3. Volatilidade e Drawdown (Lado a Lado)
    c_vol, c_dd = st.columns(2)
    
    with c_vol:
        vol_cart = portfolio_ret.rolling(21).std() * (252**0.5) * 100
        if "^BVSP" in prices.columns:
            vol_ibov = prices["^BVSP"].pct_change().rolling(21).std() * (252**0.5) * 100
        else:
            vol_ibov = pd.Series(0, index=vol_cart.index)

        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=vol_cart.index, y=vol_cart, name="Vol. Carteira", line=dict(color="#FFFFFF", width=2)))
        fig_vol.add_trace(go.Scatter(x=vol_ibov.index, y=vol_ibov, name="Vol. Ibov", line=dict(color="#FF9900", width=2)))
        
        fig_vol.update_layout(
            title=dict(text='Volatilidade (21d)', x=0, font=dict(size=14, color='white'), y=1),
            template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300, 
            legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="left", x=0), xaxis=dict(showgrid=False, fixedrange=True),
            yaxis=dict(showgrid=True, gridcolor="#333", side="right", fixedrange=True),
            dragmode=False, margin=dict(l=0, r=0, t=40, b=40)
        )
        st.plotly_chart(fig_vol, use_container_width=True, config={'displayModeBar': False})

    with c_dd:
        dd_cart = (portfolio_idx / portfolio_idx.cummax() - 1) * 100
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(x=dd_cart.index, y=dd_cart, name="Drawdown", line=dict(color="#FFFFFF", width=2), fill='tozeroy', fillcolor='rgba(255, 75, 75, 0.1)'))
        
        fig_dd.update_layout(
            title=dict(text='Drawdown (%)', x=0, font=dict(size=14, color='white'), y=1),
            template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300, showlegend=False,
            xaxis=dict(showgrid=False, fixedrange=True),
            yaxis=dict(showgrid=True, gridcolor="#333", side="right", fixedrange=True),
            dragmode=False, margin=dict(l=0, r=0, t=40, b=40)
        )
        st.plotly_chart(fig_dd, use_container_width=True, config={'displayModeBar': False})

    # --- 4. SHARPE E SETORES (NOVOS GRÁFICOS) ---
    c_sharpe, c_setor = st.columns(2)

    with c_sharpe:
        # Calcular Taxa Livre de Risco (Selic) via DB_MACRO
        info_selic = DB_MACRO["Taxa Selic"]
        # Puxa desde o inicio da carteira
        df_selic = get_macro_data("Taxa Selic", info_selic, start_date=start_date)
        
        # Cria Série de Retorno Livre de Risco Diário
        # Selic Meta é % a.a. -> Converter para diário: (1 + taxa/100)^(1/252) - 1
        if not df_selic.empty:
            df_selic['Data'] = pd.to_datetime(df_selic['Data'], dayfirst=True)
            df_selic = df_selic.set_index('Data').reindex(portfolio_ret.index).ffill().fillna(0)
            rf_daily = (1 + df_selic['Valor'] / 100) ** (1/252) - 1
        else:
            rf_daily = pd.Series(0, index=portfolio_ret.index)

        # Cálculo do Sharpe Rolling (Janela 30 dias)
        excess_ret = portfolio_ret - rf_daily
        rolling_mean = excess_ret.rolling(window=30).mean()
        rolling_std = portfolio_ret.rolling(window=30).std()
        sharpe_rolling = (rolling_mean / rolling_std) * (252 ** 0.5) # Anualizado

        fig_sharpe = go.Figure()
        fig_sharpe.add_trace(go.Scatter(x=sharpe_rolling.index, y=sharpe_rolling, name="Índice Sharpe (30d)", line=dict(color="#FFFFFF", width=2)))
        
        fig_sharpe.update_layout(
            title=dict(text='Índice Sharpe (30d Rolling)', x=0, font=dict(size=14, color='white'), y=1),
            template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300, 
            showlegend=False, xaxis=dict(showgrid=False, fixedrange=True),
            yaxis=dict(showgrid=True, gridcolor="#333", side="right", fixedrange=True),
            dragmode=False, margin=dict(l=0, r=0, t=40, b=40)
        )
        st.plotly_chart(fig_sharpe, use_container_width=True, config={'displayModeBar': False})

    with c_setor:
        # Dicionário de Setores para o Gráfico
        MAPA_SETORES_GRAFICO = {
            "WEGE3.SA": "Capital Goods", "EQTL3.SA": "Utilities", "MULT3.SA": "Malls",
            "RENT3.SA": "Transport & Logistics", "LEVE3.SA": "Capital Goods", "ITUB3.SA": "Banks & Non-banks",
            "EGIE3.SA": "Utilities", "RADL3.SA": "Retail & Consumer Goods", "SMFT3.SA": "Retail & Consumer Goods",
            "MDIA3.SA": "Agribusiness", "BBSE3.SA": "Banks & Non-banks", "LREN3.SA": "Retail & Consumer Goods",
            "BPAC3.SA": "Banks & Non-banks", "VIVT3.SA": "Tech, Media & Telecom", "ASAI3.SA": "Retail & Consumer Goods",
            "UNIP3.SA": "Chemicals", "PSSA3.SA": "Banks & Non-banks", "PRIO3.SA": "Oil & Gas",
            "VULC3.SA": "Retail & Consumer Goods"
        }
        
        # Calcular alocação atual
        current_prices = prices.iloc[-1]
        current_qtd = qtd_atual
        
        alloc_data = []
        total_val = 0
        for t, q in current_qtd.items():
            if t in current_prices:
                val = current_prices[t] * q
                sector = MAPA_SETORES_GRAFICO.get(t, "Outros")
                alloc_data.append({"Setor": sector, "Valor": val})
                total_val += val
        
        if alloc_data:
            df_alloc = pd.DataFrame(alloc_data)
            df_sector = df_alloc.groupby("Setor")["Valor"].sum().sort_values(ascending=True)
            df_sector_pct = (df_sector / total_val) * 100
            
            fig_sec = go.Figure(go.Bar(
                x=df_sector_pct.values,
                y=df_sector_pct.index,
                orientation='h',
                marker=dict(color='#FF9900'),
                text=[f"{v:.1f}%" for v in df_sector_pct.values],
                textposition='auto',
                textfont=dict(size=20, color='#FFFFFF')
            ))
            
            fig_sec.update_layout(
                title=dict(text='Alocação por Setor', x=0, font=dict(size=14, color='white'), y=1),
                template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300,
                xaxis=dict(showgrid=False, showticklabels=False, fixedrange=True),
                yaxis=dict(showgrid=False, tickfont=dict(color='white'), fixedrange=True),
                margin=dict(l=0, r=0, t=40, b=40), dragmode=False
            )
            st.plotly_chart(fig_sec, use_container_width=True, config={'displayModeBar': False})


    # --- TABELA DE RENTABILIDADE (MÊS A MÊS + ACUMULADO) ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Prepara dados diários
    ret_daily_port = portfolio_ret
    if "^BVSP" in prices.columns:
        ret_daily_ibov = prices["^BVSP"].pct_change().fillna(0)
    else:
        ret_daily_ibov = pd.Series(0, index=portfolio_ret.index)

    # Prepara dados mensais para preencher a tabela
    ret_m_port = ret_daily_port.resample('ME').apply(lambda x: (1 + x).prod() - 1) * 100
    ret_m_ibov = ret_daily_ibov.resample('ME').apply(lambda x: (1 + x).prod() - 1) * 100

    def make_pivot(series):
        df = series.to_frame(name='ret')
        df['ano'] = df.index.year
        df['mes'] = df.index.month
        return df.pivot(index='ano', columns='mes', values='ret')

    piv_port = make_pivot(ret_m_port)
    piv_ibov = make_pivot(ret_m_ibov)
    
    # Cabeçalho da Tabela
    html_rent = ['<table class="rent-table"><tr><th>ANO</th>']
    month_names = {1:'JAN', 2:'FEV', 3:'MAR', 4:'ABR', 5:'MAI', 6:'JUN', 7:'JUL', 8:'AGO', 9:'SET', 10:'OUT', 11:'NOV', 12:'DEZ'}
    for i in range(1, 13): html_rent.append(f'<th>{month_names[i]}</th>')
    html_rent.append('<th>ANO</th><th>ACUM.</th></tr>')

    # Anos em ordem decrescente
    years = sorted(piv_port.index, reverse=True)
    
    for y in years:
        # Calcular Totais do Ano
        d_p_y = ret_daily_port[ret_daily_port.index.year == y]
        d_i_y = ret_daily_ibov[ret_daily_ibov.index.year == y]
        total_y_port = ((1 + d_p_y).prod() - 1) * 100
        total_y_ibov = ((1 + d_i_y).prod() - 1) * 100

        # Calcular Acumulado (desde o início até o fim deste ano)
        d_p_cum = ret_daily_port[ret_daily_port.index <= d_p_y.index[-1]]
        d_i_cum = ret_daily_ibov[ret_daily_ibov.index <= d_i_y.index[-1]]
        cum_port = ((1 + d_p_cum).prod() - 1) * 100
        cum_ibov = ((1 + d_i_cum).prod() - 1) * 100

        # Linha Carteira
        html_rent.append(f'<tr><td style="text-align:left; font-weight:bold; color:#FFF; border:1px solid #222;">Carteira {y}</td>')
        for m in range(1, 13):
            val = piv_port.loc[y, m] if m in piv_port.columns else np.nan
            if pd.isna(val) or (y == years[0] and m > datetime.now().month): # Check futuro simples
                html_rent.append('<td>-</td>')
            else:
                color = "#00FF00" if val > 0 else ("#FF4B4B" if val < 0 else "#FFF")
                html_rent.append(f'<td style="color:{color}">{val:.2f}%</td>')
        
        # Totais Carteira
        c_ano = "#00FF00" if total_y_port > 0 else ("#FF4B4B" if total_y_port < 0 else "#FFF")
        c_cum = "#00FF00" if cum_port > 0 else ("#FF4B4B" if cum_port < 0 else "#FFF")
        html_rent.append(f'<td style="font-weight:bold; color:{c_ano}">{total_y_port:.2f}%</td>')
        html_rent.append(f'<td style="font-weight:bold; color:{c_cum}">{cum_port:.2f}%</td></tr>')

        # Linha Ibovespa
        html_rent.append(f'<tr><td style="text-align:left; font-weight:bold; color:#DAA520; border:1px solid #222;">Ibovespa {y}</td>')
        for m in range(1, 13):
            val = piv_ibov.loc[y, m] if m in piv_ibov.columns else np.nan
            if pd.isna(val) or (y == years[0] and m > datetime.now().month):
                html_rent.append('<td>-</td>')
            else:
                color = "#00FF00" if val > 0 else ("#FF4B4B" if val < 0 else "#FFF")
                html_rent.append(f'<td style="color:{color}">{val:.2f}%</td>')
        
        # Totais Ibovespa
        c_ano_i = "#00FF00" if total_y_ibov > 0 else ("#FF4B4B" if total_y_ibov < 0 else "#FFF")
        c_cum_i = "#00FF00" if cum_ibov > 0 else ("#FF4B4B" if cum_ibov < 0 else "#FFF")
        html_rent.append(f'<td style="font-weight:bold; color:{c_ano_i}">{total_y_ibov:.2f}%</td>')
        html_rent.append(f'<td style="font-weight:bold; color:{c_cum_i}">{cum_ibov:.2f}%</td></tr>')

    html_rent.append('</table>')
    st.markdown("".join(html_rent), unsafe_allow_html=True)
    
    # Stop para não carregar a parte genérica (botão e tabela antiga)
    st.stop()

elif aba_selecionada == "Índices":
    headers, t_list = ["Ticker", "Preço"] + cols_base, INDICES_LIST
else:
    headers, t_list = ["Ticker", "Preço"] + cols_base, []
    for s, ticks in SETORES_ACOMPANHAMENTO.items():
        t_list.append({"setor": s})
        t_list.extend(ticks)

tickers_da_aba = [tk for tk in t_list if isinstance(tk, str)]

with st.popover("GRÁFICOS (COTAÇÕES)"):
    col_pop1, col_pop2 = st.columns(2)
    for i, tk in enumerate(tickers_da_aba):
        target_col = col_pop1 if i % 2 == 0 else col_pop2
        if target_col.button(tk, key=f"btn_{tk}", use_container_width=True):
            exibir_grafico_popup(tk, master_data)

html_d_list = [f'<div class="desktop-view"><table class="list-container"><tr class="list-header">']
for h in headers: html_d_list.append(f'<th>{h}</th>')
html_d_list.append('</tr>')
html_m_list = ['<div class="mobile-view">']

for t in t_list:
    if isinstance(t, dict):
        s_n = t["setor"].upper()
        html_d_list.append(f'<tr class="sector-row"><td colspan="{len(headers)}">{s_n}</td></tr>')
        html_m_list.append(f'<div class="mob-sector">{s_n}</div>')
        continue
    
    if t not in master_data.columns.levels[0]: continue
    
    try:
        cl = master_data[t]['Close'].dropna()
        if cl.empty: continue
        p = float(cl.iloc[-1])
        sym = "R$ " if (t == "^BVSP" or ".SA" in t) else ("" if aba_selecionada == "Índices" else "US$ ")
        
        v_h, v_30, v_6m, v_12, v_ytd, v_5a = (
            calc_variation(cl, 1), calc_variation(cl, 21), 
            calc_variation(cl, 126), calc_variation(cl, 252), 
            calc_variation(cl, ytd=True), calc_variation(cl, 1260)
        )

        html_d_list.append(f'<tr class="list-row"><td><span class="ticker-link">{t}</span></td><td>{format_val_html(p, sym=sym)}</td>')
        
        if aba_selecionada == "Cobertura":
            alv = COBERTURA[t]["Alvo"]
            html_d_list.append(f'<td>{COBERTURA[t]["Rec"]}</td><td>{format_val_html(alv, sym=sym)}</td><td>{format_val_html((alv/p-1)*100, is_pct=True)}</td>')
        
        if aba_selecionada == "Carteira pessoal" and not df_p.empty:
            row_data = df_p[df_p["Ticker"] == t].iloc[0]
            html_d_list.append(f'<td>{int(row_data["Qtd"])}</td>')
            html_d_list.append(f'<td>{format_val_html(row_data["Total"], sym=sym)}</td>')
            html_d_list.append(f'<td>{format_val_html(row_data["Peso %"], is_pct=True, force_white=True)}</td>')
        
        for val in [v_h, v_30, v_6m, v_12, v_ytd, v_5a]:
            html_d_list.append(f'<td>{format_val_html(val, is_pct=True)}</td>')
        html_d_list.append('</tr>')

        f_p = "{:,.2f}".format(p).replace(",", "X").replace(".", ",").replace("X", ".")
        html_m_list.append(f'<details><summary><div class="mob-header-left"><span class="mob-ticker">{t}</span></div><div class="mob-header-right"><span class="mob-price">{sym}{f_p}</span><span class="mob-today">{format_val_html(v_h, is_pct=True)}</span></div></summary><div class="mob-content"><div class="mob-grid">')
        if aba_selecionada == "Cobertura":
            alv = COBERTURA[t]["Alvo"]
            html_m_list.append(f'<div class="mob-item"><span class="mob-label">REC</span><span class="mob-val">{COBERTURA[t]["Rec"]}</span></div><div class="mob-item"><span class="mob-label">ALVO</span><span class="mob-val">{format_val_html(alv, sym=sym)}</span></div><div class="mob-item"><span class="mob-label">UPSIDE</span><span class="mob-val">{format_val_html((alv/p-1)*100, is_pct=True)}</span></div>')
        if aba_selecionada == "Carteira pessoal" and not df_p.empty:
            row_data = df_p[df_p["Ticker"] == t].iloc[0]
            html_m_list.append(f'<div class="mob-item"><span class="mob-label">QTD</span><span class="mob-val">{int(row_data["Qtd"])}</span></div>')
            html_m_list.append(f'<div class="mob-item"><span class="mob-label">TOTAL</span><span class="mob-val">{format_val_html(row_data["Total"], sym=sym)}</span></div>')
            html_m_list.append(f'<div class="mob-item"><span class="mob-label">PESO</span><span class="mob-val">{format_val_html(row_data["Peso %"], is_pct=True, force_white=True)}</span></div>')
        
        periods = [("30D", v_30), ("6M", v_6m), ("12M", v_12), ("YTD", v_ytd), ("5A", v_5a)]
        for lab, val in periods:
            html_m_list.append(f'<div class="mob-item"><span class="mob-label">{lab}</span><span class="mob-val">{format_val_html(val, is_pct=True)}</span></div>')
        html_m_list.append('</div></div></details>')
    except: continue

html_d_list.append('</table></div>')
html_m_list.append('</div>')
st.markdown("".join(html_d_list) + "".join(html_m_list), unsafe_allow_html=True)
