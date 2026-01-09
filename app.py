import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuração de página
st.set_page_config(page_title="Monitor de Ações", layout="wide")

# CSS para customização (Largura do Popover e ajuste da coluna Ticker)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    div[data-testid="stDataFrame"] > div { margin-bottom: -20px; }
    div[data-testid="stPopoverBody"] { width: 750px !important; }
    
    /* Ajuste para evitar que o texto dos segmentos seja cortado */
    [data-testid="stDataFrame"] td[data-col-index="0"] {
        min-width: 250px !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 1. DICIONÁRIOS DE DADOS
# =========================================================

COBERTURA = {
    "AZZA3.SA": {"Rec": "Compra", "Alvo": 50.00}, "LREN3.SA": {"Rec": "Compra", "Alvo": 23.00},
    "MGLU3.SA": {"Rec": "Neutro", "Alvo": 10.00}, "MELI": {"Rec": "Compra", "Alvo": 2810.00},
    "ASAI3.SA": {"Rec": "Compra", "Alvo": 18.00}, "RADL3.SA": {"Rec": "Compra", "Alvo": 29.00},
    "SMFT3.SA": {"Rec": "Compra", "Alvo": 36.00}, "NATU3.SA": {"Rec": "Compra", "Alvo": 15.00},
    "AUAU3.SA": {"Rec": "Neutro", "Alvo": 3.00}, "ABEV3.SA": {"Rec": "Neutro", "Alvo": 15.00},
    "MULT3.SA": {"Rec": "Compra", "Alvo": 35.00}, "WEGE3.SA": {"Rec": "Neutro", "Alvo": 49.00},
    "RENT3.SA": {"Rec": "Compra", "Alvo": 58.00},
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

# =========================================================
# 2. FUNÇÕES DE APOIO
# =========================================================

st.sidebar.title("Navegação")
aba_selecionada = st.sidebar.radio("Selecione o Monitor:", ["Cobertura", "Acompanhamentos", "Carteira pessoal"])

def format_val(val, is_pct=False, sym=""):
    if pd.isna(val) or (val == 0 and not is_pct): return ""
    f = "{:,.2f}".format(val).replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{f}%" if is_pct else (f"{sym}{f}" if sym else f)

@st.cache_data(ttl=300)
def get_data(tickers):
    if not tickers: return None
    return yf.download(tickers, period="6y", group_by='ticker', auto_adjust=True, progress=False)

def calc_v(h, d=None, ytd=False):
    try:
        close_series = h['Close'].dropna()
        if close_series.empty: return 0.0
        curr = float(close_series.iloc[-1])
        if ytd:
            start_row = close_series.loc[f"{datetime.now().year}-01-01":]
            start = float(start_row.iloc[0]) if not start_row.empty else float(close_series.iloc[0])
        else:
            start = float(close_series.iloc[-d]) if len(close_series) >= d else float(close_series.iloc[0])
        return ((curr / start) - 1) * 100
    except: return 0.0

# =========================================================
# 3. RENDERIZAÇÃO
# =========================================================

@st.fragment(run_every=300)
def render_monitor(aba_nome):
    st.title(f"Monitor: {aba_nome}")
    
    if aba_nome == "Cobertura": t_list = list(COBERTURA.keys())
    elif aba_nome == "Acompanhamentos": t_list = [t for sub in SETORES_ACOMPANHAMENTO.values() for t in sub]
    else: t_list = list(CARTEIRA_PESSOAL_QTD.keys())
    
    data = get_data(t_list)

    c1, c2, _ = st.columns([0.1, 0.2, 0.7])
    with c1:
        if st.button("Atualizar", key=f"btn_refresh_{aba_nome}"):
            st.cache_data.clear()
            st.rerun()
    with c2:
        with st.popover("Gráficos"):
            t_sel = st.selectbox("Ativo", options=sorted(list(set(t_list))), key=f"sb_{aba_nome}")
            p_sel = st.segmented_control("Período", options=["30D", "6M", "12M", "5A", "YTD"], default="12M", key=f"sc_{aba_nome}")
            
            if t_sel:
                h_plot = data[t_sel] if len(t_list) > 1 else data
                df_all = h_plot['Close'].dropna()
                if not df_all.empty:
                    map_p = {"30D": 21, "6M": 126, "12M": 252, "5A": 1260, "YTD": "ytd"}
                    if map_p[p_sel] == "ytd":
                        df_view = df_all.loc[f"{datetime.now().year}-01-01":]
                    else:
                        d_val = map_p[p_sel]
                        df_view = df_all.iloc[-d_val:] if len(df_all) > d_val else df_all

                    v_p = ((df_view.iloc[-1] / df_view.iloc[0]) - 1) * 100 if len(df_view) > 1 else 0.0
                    color_line = "#00FF00" if v_p >= 0 else "#FF4B4B"

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df_view.index, y=df_view.values, line=dict(color=color_line, width=2.5)))
                    fig.update_layout(
                        title=f"<b>{t_sel} | {v_p:.2f}%</b>",
                        template="plotly_dark", height=380, margin=dict(l=0, r=40, t=50, b=0),
                        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#333", side="right", autorange=True),
                        autosize=True
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Construção da Tabela
    rows = []
    for t in t_list:
        try:
            h = data[t] if len(t_list) > 1 else data
            cl = h['Close'].dropna()
            p = float(cl.iloc[-1])
            row = {
                "Ticker": t, "Moeda": "R$ " if ".SA" in t or t == "^BVSP" else "$ ",
                "Preço": p, "Hoje %": ((p/cl.iloc[-2])-1)*100 if len(cl) > 1 else 0,
                "30D %": calc_v(h, 21), "6M %": calc_v(h, 126),
                "12M %": calc_v(h, 252), "YTD %": calc_v(h, ytd=True),
                "5A %": calc_v(h, 1260), "is_h": False, "ValPos": 0.0
            }
            if aba_nome == "Cobertura":
                alvo = COBERTURA[t]["Alvo"]
                row.update({"Rec": COBERTURA[t]["Rec"], "Alvo": alvo, "Upside": (alvo/p - 1)*100 if alvo > 0 else 0})
            if aba_nome == "Carteira pessoal": row["ValPos"] = p * CARTEIRA_PESSOAL_QTD[t]
            rows.append(row)
        except: continue

    df_raw = pd.DataFrame(rows)

    if aba_nome == "Carteira pessoal" and not df_raw.empty:
        df_raw["Peso %"] = (df_raw["ValPos"] / df_raw["ValPos"].sum()) * 100
        df_raw = df_raw.sort_values(by="Peso %", ascending=False)

    if aba_nome == "Acompanhamentos":
        final_rows = []
        for setor, ticks in SETORES_ACOMPANHAMENTO.items():
            final_rows.append({"Ticker": f"--- {setor.upper()} ---", "is_h": True})
            final_rows.extend([r for r in rows if r["Ticker"] in ticks])
        df_raw = pd.DataFrame(final_rows)

    if df_raw.empty: return

    df_v = df_raw.copy()
    pct_cols = ["Peso %", "Hoje %", "30D %", "6M %", "12M %", "YTD %", "5A %", "Upside"]
    
    for c in ["Preço", "Alvo"]:
        if c in df_v.columns: 
            df_v[c] = df_raw.apply(lambda r: format_val(r[c], sym=r["Moeda"]) if not r["is_h"] else "", axis=1)
    
    for c in pct_cols:
        if c in df_v.columns:
            df_v[c] = df_raw.apply(lambda r: format_val(r[c], is_pct=True) if not r["is_h"] else "", axis=1)

    def style_r(row):
        orig = df_raw.loc[row.name]
        if orig["is_h"]: return ['background-color: #262730; color: #FFA500; font-weight: bold'] * len(row)
        styles = [''] * len(row)
        for i, col in enumerate(row.index):
            if col in pct_cols and col != "Peso %":
                val = orig[col]
                styles[i] = 'color: #00FF00' if val > 0 else 'color: #FF4B4B' if val < 0 else ''
        return styles

    if aba_nome == "Cobertura":
        cols = ["Ticker", "Preço", "Rec", "Alvo", "Upside", "Hoje %", "30D %", "6M %", "12M %", "YTD %", "5A %"]
    elif aba_nome == "Carteira pessoal":
        cols = ["Ticker", "Peso %", "Preço", "Hoje %", "30D %", "6M %", "12M %", "YTD %", "5A %"]
    else:
        cols = ["Ticker", "Preço", "Hoje %", "30D %", "6M %", "12M %", "YTD %", "5A %"]

    st.caption(f"Atualização: {datetime.now().strftime('%H:%M:%S')}")
    st.dataframe(df_v[cols].style.apply(style_r, axis=1), use_container_width=True, hide_index=True, height=(len(df_v) * 35) + 38)

render_monitor(aba_selecionada)


