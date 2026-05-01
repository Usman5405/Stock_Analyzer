"""
================================================================================
  PROFESSIONAL STOCK MARKET ANALYZER  –  Streamlit Edition
  ──────────────────────────────────────────────────────────
  A production-grade web dashboard for technical stock analysis featuring:

  • Real-time OHLCV data from Yahoo Finance (yfinance)
  • RSI, MACD, Bollinger Bands, Stochastic, ATR, OBV
  • Composite Buy / Sell / Hold signal engine
  • Interactive Plotly charts (zoom, pan, hover)
  • Sleek terminal-noir dark UI with custom CSS
  • Daily / Weekly / Monthly timeframes
  • 30+ preset stocks across 5 global sectors

INSTALL & RUN:
  pip install -r requirements.txt
  streamlit run stock_analyzer_streamlit.py
================================================================================
"""

# ── Standard library ──────────────────────────────────────────────────────────
import datetime

# ── Third-party ───────────────────────────────────────────────────────────────
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG  – must be the very first Streamlit call
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Stock Analyzer Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ══════════════════════════════════════════════════════════════════════════════
#  CUSTOM CSS  – terminal-noir aesthetic
#  Deep blacks, electric cyan accent, monospace typography
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

/* ── Root tokens ── */
:root {
    --bg-0:      #080c10;
    --bg-1:      #0d1117;
    --bg-2:      #161b22;
    --bg-3:      #21262d;
    --border:    #30363d;
    --cyan:      #00e5ff;
    --cyan-dim:  #0097a7;
    --green:     #00e676;
    --red:       #ff1744;
    --yellow:    #ffd740;
    --text:      #cdd9e5;
    --muted:     #768390;
    --mono:      'Share Tech Mono', monospace;
    --sans:      'Rajdhani', sans-serif;
}

/* ── Global resets ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-0) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
[data-testid="stSidebar"] {
    background-color: var(--bg-1) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Top header bar ── */
.top-bar {
    background: linear-gradient(135deg, var(--bg-2) 0%, var(--bg-1) 100%);
    border: 1px solid var(--border);
    border-left: 4px solid var(--cyan);
    border-radius: 4px;
    padding: 18px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.top-bar h1 {
    font-family: var(--mono) !important;
    font-size: 1.6rem !important;
    color: var(--cyan) !important;
    margin: 0 !important;
    letter-spacing: 2px;
    text-shadow: 0 0 20px rgba(0,229,255,0.4);
}
.top-bar p {
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
    color: var(--muted) !important;
    margin: 4px 0 0 0 !important;
    letter-spacing: 1px;
}

/* ── Metric cards ── */
.metric-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.metric-card {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 20px;
    flex: 1;
    min-width: 130px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--cyan);
    opacity: 0.6;
}
.metric-card .label {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-card .value {
    font-family: var(--mono);
    font-size: 1.3rem;
    color: var(--text);
    font-weight: bold;
}
.metric-card .sub {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--muted);
    margin-top: 4px;
}
.metric-card.green::before { background: var(--green); }
.metric-card.red::before   { background: var(--red); }
.metric-card.yellow::before{ background: var(--yellow); }
.metric-card.cyan::before  { background: var(--cyan); }

/* ── Signal badge ── */
.signal-box {
    border-radius: 8px;
    padding: 24px 32px;
    text-align: center;
    margin-bottom: 20px;
    border: 1px solid var(--border);
}
.signal-box.buy  { background: rgba(0,230,118,0.08); border-color: var(--green); }
.signal-box.sell { background: rgba(255,23,68,0.08);  border-color: var(--red); }
.signal-box.hold { background: rgba(255,215,64,0.08); border-color: var(--yellow); }
.signal-box .sig-label {
    font-family: var(--mono);
    font-size: 0.7rem;
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
}
.signal-box .sig-value {
    font-family: var(--mono);
    font-size: 3.5rem;
    font-weight: bold;
    letter-spacing: 6px;
    line-height: 1.1;
    text-shadow: 0 0 30px currentColor;
}
.signal-box.buy  .sig-value { color: var(--green); }
.signal-box.sell .sig-value { color: var(--red); }
.signal-box.hold .sig-value { color: var(--yellow); }
.signal-box .sig-score {
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 8px;
}

/* ── Section headers ── */
.section-header {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--cyan);
    letter-spacing: 3px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
}

/* ── Indicator table ── */
.ind-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.ind-cell {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 10px 14px;
}
.ind-cell .ind-name  { font-family: var(--mono); font-size: 0.65rem; color: var(--muted); letter-spacing: 1px; }
.ind-cell .ind-value { font-family: var(--mono); font-size: 1.05rem; color: var(--cyan); margin-top: 4px; }
.ind-cell .ind-desc  { font-family: var(--sans);  font-size: 0.7rem;  color: var(--muted); margin-top: 2px; }

/* ── Report block ── */
.report-block {
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px 24px;
    font-family: var(--mono);
    font-size: 0.78rem;
    color: var(--text);
    line-height: 1.8;
    white-space: pre-wrap;
    overflow-x: auto;
}

/* ── Sidebar widgets ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div > input {
    background: var(--bg-3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    border-radius: 4px !important;
}
[data-testid="stRadio"] label { font-family: var(--mono) !important; font-size: 0.85rem !important; }
[data-testid="stSlider"] { font-family: var(--mono) !important; }

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--cyan) !important;
    color: var(--cyan) !important;
    font-family: var(--mono) !important;
    font-size: 0.85rem !important;
    letter-spacing: 2px !important;
    border-radius: 4px !important;
    padding: 10px 24px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0,229,255,0.1) !important;
    box-shadow: 0 0 20px rgba(0,229,255,0.2) !important;
}

/* ── Tab styling ── */
[data-baseweb="tab-list"] { background: var(--bg-2) !important; border-radius: 6px; gap: 2px; padding: 4px; }
[data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px !important;
    color: var(--muted) !important;
    background: transparent !important;
    border-radius: 4px !important;
}
[aria-selected="true"][data-baseweb="tab"] { color: var(--cyan) !important; background: var(--bg-3) !important; }
[data-baseweb="tab-panel"] { background: transparent !important; padding: 20px 0 0 0 !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-1); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 – PRESET STOCK CATALOGUE
# ══════════════════════════════════════════════════════════════════════════════

STOCK_CATALOGUE = {
    "Technology 💻": [
        ("Apple Inc.",        "AAPL"),
        ("Microsoft Corp.",   "MSFT"),
        ("NVIDIA Corp.",      "NVDA"),
        ("Alphabet / Google", "GOOGL"),
        ("Amazon.com",        "AMZN"),
        ("Meta Platforms",    "META"),
        ("Tesla Inc.",        "TSLA"),
        ("TSMC",              "TSM"),
    ],
    "Finance 🏦": [
        ("JPMorgan Chase",    "JPM"),
        ("Goldman Sachs",     "GS"),
        ("Berkshire Hathaway","BRK-B"),
        ("Visa Inc.",         "V"),
        ("Mastercard",        "MA"),
    ],
    "Energy ⚡": [
        ("ExxonMobil",        "XOM"),
        ("Chevron",           "CVX"),
        ("Shell PLC",         "SHEL"),
        ("BP PLC",            "BP"),
    ],
    "Healthcare 🏥": [
        ("Johnson & Johnson", "JNJ"),
        ("Pfizer Inc.",       "PFE"),
        ("UnitedHealth",      "UNH"),
        ("Eli Lilly",         "LLY"),
    ],
    "Pakistan PSX 🇵🇰": [
        ("Habib Bank Ltd",    "HBL.KA"),
        ("OGDCL",             "OGDC.KA"),
        ("Lucky Cement",      "LUCK.KA"),
        ("Engro Corp.",       "ENGRO.KA"),
    ],
}

INTERVAL_MAP = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}
PERIOD_MAP   = {"Daily": "2y", "Weekly": "5y",  "Monthly": "10y"}


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 – DATA FETCHER
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)   # cache 5 minutes
def fetch_data(ticker: str, frequency: str) -> pd.DataFrame:
    """Download OHLCV from Yahoo Finance and return a clean DataFrame."""
    interval = INTERVAL_MAP[frequency]
    period   = PERIOD_MAP[frequency]
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
    if df is None or df.empty:
        raise ValueError(f"No data for '{ticker}'. Check the symbol.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open","High","Low","Close","Volume"]].dropna().sort_index()
    return df


@st.cache_data(ttl=600, show_spinner=False)
def fetch_info(ticker: str) -> dict:
    """Fetch company metadata from Yahoo Finance."""
    try:
        info = yf.Ticker(ticker).info
        return {
            "name":       info.get("longName", ticker),
            "sector":     info.get("sector", "N/A"),
            "industry":   info.get("industry", "N/A"),
            "market_cap": info.get("marketCap"),
            "pe_ratio":   info.get("trailingPE"),
            "52w_high":   info.get("fiftyTwoWeekHigh"),
            "52w_low":    info.get("fiftyTwoWeekLow"),
            "currency":   info.get("currency", "USD"),
            "website":    info.get("website", ""),
        }
    except Exception:
        return {"name": ticker, "sector": "N/A", "industry": "N/A",
                "market_cap": None, "pe_ratio": None,
                "52w_high": None, "52w_low": None,
                "currency": "USD", "website": ""}


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 – TECHNICAL ANALYSIS ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def compute_indicators(df: pd.DataFrame, rsi_period: int = 14) -> pd.DataFrame:
    """
    Compute all technical indicators and return enriched DataFrame.

    Indicators computed:
      RSI, MACD, Bollinger Bands, SMA 20/50/200,
      EMA 9/21, Stochastic %K/%D, ATR, OBV, Volume SMA,
      Composite signal score + BUY/HOLD/SELL label
    """
    d = df.copy()

    # ── RSI ──────────────────────────────────────────────────────────────────
    delta    = d["Close"].diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
    rs       = avg_gain / avg_loss.replace(0, np.nan)
    d["RSI"] = 100 - (100 / (1 + rs))

    # ── MACD ─────────────────────────────────────────────────────────────────
    ema12           = d["Close"].ewm(span=12, adjust=False).mean()
    ema26           = d["Close"].ewm(span=26, adjust=False).mean()
    d["MACD"]       = ema12 - ema26
    d["MACD_Sig"]   = d["MACD"].ewm(span=9, adjust=False).mean()
    d["MACD_Hist"]  = d["MACD"] - d["MACD_Sig"]

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    sma20           = d["Close"].rolling(20).mean()
    std20           = d["Close"].rolling(20).std()
    d["BB_Mid"]     = sma20
    d["BB_Up"]      = sma20 + 2 * std20
    d["BB_Lo"]      = sma20 - 2 * std20
    bw              = (d["BB_Up"] - d["BB_Lo"]).replace(0, np.nan)
    d["BB_PctB"]    = (d["Close"] - d["BB_Lo"]) / bw
    d["BB_BW"]      = bw / sma20.replace(0, np.nan)

    # ── Moving Averages ───────────────────────────────────────────────────────
    for p in [20, 50, 200]:
        d[f"SMA_{p}"] = d["Close"].rolling(p).mean()
    for p in [9, 21]:
        d[f"EMA_{p}"] = d["Close"].ewm(span=p, adjust=False).mean()

    # ── Stochastic ────────────────────────────────────────────────────────────
    lo14         = d["Low"].rolling(14).min()
    hi14         = d["High"].rolling(14).max()
    denom        = (hi14 - lo14).replace(0, np.nan)
    d["Stoch_K"] = (d["Close"] - lo14) / denom * 100
    d["Stoch_D"] = d["Stoch_K"].rolling(3).mean()

    # ── ATR ───────────────────────────────────────────────────────────────────
    prev_c    = d["Close"].shift(1)
    tr        = pd.concat([d["High"]-d["Low"],
                           (d["High"]-prev_c).abs(),
                           (d["Low"] -prev_c).abs()], axis=1).max(axis=1)
    d["ATR"]      = tr.ewm(com=13, min_periods=14).mean()
    d["ATR_Pct"]  = d["ATR"] / d["Close"] * 100

    # ── Volume ────────────────────────────────────────────────────────────────
    d["Vol_SMA20"]  = d["Volume"].rolling(20).mean()
    d["Vol_Ratio"]  = d["Volume"] / d["Vol_SMA20"].replace(0, np.nan)
    direction       = np.sign(d["Close"].diff())
    d["OBV"]        = (direction * d["Volume"]).cumsum()

    # ── Composite Signal ──────────────────────────────────────────────────────
    score = pd.Series(0.0, index=d.index)
    score += (d["RSI"] < 30).astype(int)
    score -= (d["RSI"] > 70).astype(int)
    macd_up   = (d["MACD"] > d["MACD_Sig"]) & (d["MACD"].shift(1) <= d["MACD_Sig"].shift(1))
    macd_down = (d["MACD"] < d["MACD_Sig"]) & (d["MACD"].shift(1) >= d["MACD_Sig"].shift(1))
    score    += macd_up.astype(int)
    score    -= macd_down.astype(int)
    score    += (d["BB_PctB"] < 0.05).astype(int)
    score    -= (d["BB_PctB"] > 0.95).astype(int)
    score    += (d["Close"] > d["SMA_50"]).astype(int)
    score    -= (d["Close"] < d["SMA_50"]).astype(int)
    score    += (d["Stoch_K"] < 20).astype(int)
    score    -= (d["Stoch_K"] > 80).astype(int)

    d["Score"]  = score
    d["Signal"] = score.apply(lambda s: "BUY" if s > 2 else ("SELL" if s < -2 else "HOLD"))
    return d


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 – PLOTLY CHART BUILDER
# ══════════════════════════════════════════════════════════════════════════════

PLOTLY_THEME = dict(
    paper_bgcolor = "#080c10",
    plot_bgcolor  = "#0d1117",
    font          = dict(family="'Share Tech Mono', monospace", color="#cdd9e5", size=11),
    gridcolor     = "#21262d",
    linecolor     = "#30363d",
)

def build_chart(df: pd.DataFrame, ticker: str, freq: str) -> go.Figure:
    """
    Build a 4-panel interactive Plotly chart:
      Row 1 (60%): Candlestick + Bollinger Bands + SMA 50/200 + Signal markers
      Row 2 (15%): RSI with shaded zones
      Row 3 (15%): MACD + Signal + Histogram
      Row 4 (10%): Volume bars + SMA20
    """
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.15, 0.18, 0.12],
        vertical_spacing=0.02,
        subplot_titles=("", "RSI", "MACD", "Volume"),
    )

    x = df.index

    # ── Row 1: Price ──────────────────────────────────────────────────────────
    # Bollinger Band fill
    fig.add_trace(go.Scatter(x=x, y=df["BB_Up"], line=dict(width=0),
                             showlegend=False, hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["BB_Lo"], line=dict(width=0),
                             fill="tonexty",
                             fillcolor="rgba(0,229,255,0.05)",
                             name="Bollinger Band",
                             hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["BB_Up"], line=dict(color="#00e5ff", width=0.8, dash="dot"),
                             name="BB Upper", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["BB_Lo"], line=dict(color="#00e5ff", width=0.8, dash="dot"),
                             name="BB Lower", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["BB_Mid"], line=dict(color="#4a5568", width=0.8, dash="dash"),
                             name="BB Mid / SMA20"), row=1, col=1)

    # SMA lines
    if df["SMA_50"].notna().any():
        fig.add_trace(go.Scatter(x=x, y=df["SMA_50"],
                                 line=dict(color="#ffd740", width=1.2),
                                 name="SMA 50"), row=1, col=1)
    if df["SMA_200"].notna().any():
        fig.add_trace(go.Scatter(x=x, y=df["SMA_200"],
                                 line=dict(color="#ce93d8", width=1.2),
                                 name="SMA 200"), row=1, col=1)

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=x,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        increasing=dict(line=dict(color="#00e676", width=1),
                        fillcolor="rgba(0,230,118,0.8)"),
        decreasing=dict(line=dict(color="#ff1744", width=1),
                        fillcolor="rgba(255,23,68,0.8)"),
        name="OHLC",
    ), row=1, col=1)

    # Buy / Sell signal markers
    buy_mask  = df["Signal"] == "BUY"
    sell_mask = df["Signal"] == "SELL"
    if buy_mask.any():
        fig.add_trace(go.Scatter(
            x=df.index[buy_mask],
            y=df["Low"][buy_mask] * 0.994,
            mode="markers",
            marker=dict(symbol="triangle-up", size=10,
                        color="#00e676", line=dict(color="#000", width=0.5)),
            name="BUY Signal",
        ), row=1, col=1)
    if sell_mask.any():
        fig.add_trace(go.Scatter(
            x=df.index[sell_mask],
            y=df["High"][sell_mask] * 1.006,
            mode="markers",
            marker=dict(symbol="triangle-down", size=10,
                        color="#ff1744", line=dict(color="#000", width=0.5)),
            name="SELL Signal",
        ), row=1, col=1)

    # ── Row 2: RSI ────────────────────────────────────────────────────────────
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,23,68,0.06)",
                  line_width=0, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,230,118,0.06)",
                  line_width=0, row=2, col=1)
    fig.add_hline(y=70, line=dict(color="#ff1744", width=0.8, dash="dash"),
                  row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#00e676", width=0.8, dash="dash"),
                  row=2, col=1)
    fig.add_hline(y=50, line=dict(color="#4a5568", width=0.6, dash="dot"),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["RSI"],
                             line=dict(color="#00e5ff", width=1.5),
                             name="RSI", fill="tozeroy",
                             fillcolor="rgba(0,229,255,0.04)"), row=2, col=1)

    # ── Row 3: MACD ───────────────────────────────────────────────────────────
    hist_colors = ["rgba(0,230,118,0.7)" if v >= 0 else "rgba(255,23,68,0.7)"
                   for v in df["MACD_Hist"].fillna(0)]
    fig.add_trace(go.Bar(x=x, y=df["MACD_Hist"],
                         marker_color=hist_colors,
                         name="MACD Histogram", showlegend=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["MACD"],
                             line=dict(color="#00e5ff", width=1.3),
                             name="MACD Line"), row=3, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["MACD_Sig"],
                             line=dict(color="#ffd740", width=1.3),
                             name="Signal Line"), row=3, col=1)

    # ── Row 4: Volume ─────────────────────────────────────────────────────────
    vol_colors = ["rgba(0,230,118,0.55)" if c >= o else "rgba(255,23,68,0.55)"
                  for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(x=x, y=df["Volume"],
                         marker_color=vol_colors,
                         name="Volume", showlegend=False), row=4, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["Vol_SMA20"],
                             line=dict(color="#ffd740", width=1.0, dash="dot"),
                             name="Vol SMA20"), row=4, col=1)

    # ── Layout ────────────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor=PLOTLY_THEME["paper_bgcolor"],
        plot_bgcolor =PLOTLY_THEME["plot_bgcolor"],
        font         =PLOTLY_THEME["font"],
        height       =820,
        margin       =dict(l=10, r=10, t=30, b=10),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h", x=0, y=1.02,
            bgcolor="rgba(13,17,23,0.8)",
            bordercolor="#30363d", borderwidth=1,
            font=dict(size=10),
        ),
        hoverlabel=dict(
            bgcolor="#161b22", bordercolor="#30363d",
            font=dict(family="'Share Tech Mono', monospace", size=11),
        ),
    )
    # Style all axes
    axis_style = dict(
        gridcolor="#21262d", linecolor="#30363d",
        tickfont=dict(size=10), showgrid=True,
    )
    for i in range(1, 5):
        fig.update_xaxes(axis_style, row=i, col=1)
        fig.update_yaxes(axis_style, row=i, col=1)

    fig.update_yaxes(range=[0, 100], row=2, col=1)
    fig.update_layout(title=dict(
        text=f"<b>{ticker}</b>  ·  {freq} Chart",
        font=dict(family="'Share Tech Mono', monospace",
                  color="#00e5ff", size=14),
        x=0.5,
    ))
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 – HELPER RENDERERS
# ══════════════════════════════════════════════════════════════════════════════

def fmt_large(v):
    if v is None: return "N/A"
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9:  return f"${v/1e9:.2f}B"
    if v >= 1e6:  return f"${v/1e6:.2f}M"
    return f"${v:,.0f}"

def safe(v, fmt=".2f"):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "N/A"
    return f"{v:{fmt}}"

def render_metric_cards(latest: dict, info: dict):
    close   = latest["Close"]
    rsi     = latest.get("RSI", float("nan"))
    signal  = latest.get("Signal", "HOLD")
    atr_pct = latest.get("ATR_Pct", float("nan"))
    vol_r   = latest.get("Vol_Ratio", float("nan"))

    sig_color = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}.get(signal, "cyan")

    cards = [
        ("CLOSE PRICE", f"{close:.4f}", info.get("currency","USD"),   "cyan"),
        ("RSI (14)",    safe(rsi,".1f"), "overbought >70 · oversold <30", "cyan"),
        ("SIGNAL",      signal,          f"score {latest.get('Score',0):+.0f}", sig_color),
        ("ATR %",       safe(atr_pct,".2f")+"%", "volatility measure",  "yellow"),
        ("VOL RATIO",   safe(vol_r,".2f")+"×",   "vs 20-day avg",       "cyan"),
        ("MARKET CAP",  fmt_large(info.get("market_cap")), info.get("sector",""), "cyan"),
    ]

    html = '<div class="metric-row">'
    for label, val, sub, color in cards:
        html += f"""
        <div class="metric-card {color}">
            <div class="label">{label}</div>
            <div class="value">{val}</div>
            <div class="sub">{sub}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_signal_box(latest: dict):
    signal = latest.get("Signal", "HOLD")
    score  = latest.get("Score", 0)
    css    = signal.lower()
    st.markdown(f"""
    <div class="signal-box {css}">
        <div class="sig-label">COMPOSITE SIGNAL</div>
        <div class="sig-value">{signal}</div>
        <div class="sig-score">Score: {score:+.0f} &nbsp;|&nbsp; Threshold: &gt;+2 BUY · &lt;-2 SELL</div>
    </div>
    """, unsafe_allow_html=True)


def render_indicator_grid(latest: dict):
    def cell(name, val, desc):
        return f"""<div class="ind-cell">
            <div class="ind-name">{name}</div>
            <div class="ind-value">{val}</div>
            <div class="ind-desc">{desc}</div>
        </div>"""

    rsi    = latest.get("RSI", float("nan"))
    macd   = latest.get("MACD", float("nan"))
    msig   = latest.get("MACD_Sig", float("nan"))
    mhist  = latest.get("MACD_Hist", float("nan"))
    pctb   = latest.get("BB_PctB", float("nan"))
    bbup   = latest.get("BB_Up", float("nan"))
    bblo   = latest.get("BB_Lo", float("nan"))
    sma20  = latest.get("SMA_20", float("nan"))
    sma50  = latest.get("SMA_50", float("nan"))
    sma200 = latest.get("SMA_200", float("nan"))
    ema9   = latest.get("EMA_9", float("nan"))
    stk    = latest.get("Stoch_K", float("nan"))
    std    = latest.get("Stoch_D", float("nan"))
    atr    = latest.get("ATR", float("nan"))
    atrp   = latest.get("ATR_Pct", float("nan"))
    volr   = latest.get("Vol_Ratio", float("nan"))

    rsi_state = "OVERSOLD" if rsi < 30 else ("OVERBOUGHT" if rsi > 70 else "NEUTRAL")

    rows = [
        ("RSI (14)",      f"{safe(rsi,'.1f')}",          rsi_state),
        ("MACD",          f"{safe(macd,'.5f')}",          "12/26 EMA diff"),
        ("MACD Signal",   f"{safe(msig,'.5f')}",          "9-period EMA of MACD"),
        ("MACD Hist",     f"{safe(mhist,'+.5f')}",        "MACD − Signal"),
        ("BB %B",         f"{safe(pctb,'.3f')}",          "0=lower · 1=upper"),
        ("BB Upper",      f"{safe(bbup,'.4f')}",          "+2σ from SMA20"),
        ("BB Lower",      f"{safe(bblo,'.4f')}",          "−2σ from SMA20"),
        ("SMA 20",        f"{safe(sma20,'.4f')}",         "20-period simple MA"),
        ("SMA 50",        f"{safe(sma50,'.4f')}",         "50-period simple MA"),
        ("SMA 200",       f"{safe(sma200,'.4f')}",        "200-period simple MA"),
        ("EMA 9",         f"{safe(ema9,'.4f')}",          "9-period exponential MA"),
        ("Stoch %K",      f"{safe(stk,'.1f')}",           "overbought >80 · oversold <20"),
        ("Stoch %D",      f"{safe(std,'.1f')}",           "3-period SMA of %K"),
        ("ATR (14)",      f"{safe(atr,'.4f')}",           "avg true range"),
        ("ATR %",         f"{safe(atrp,'.2f')}%",         "ATR as % of price"),
        ("Volume Ratio",  f"{safe(volr,'.2f')}×",         "vs 20-day avg volume"),
    ]

    html = '<div class="ind-grid">'
    for name, val, desc in rows:
        html += cell(name, val, desc)
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_report(ticker, freq, info, latest, df):
    """Detailed textual signal report."""
    close   = latest["Close"]
    rsi     = latest.get("RSI", float("nan"))
    macd    = latest.get("MACD", float("nan"))
    msig    = latest.get("MACD_Sig", float("nan"))
    stk     = latest.get("Stoch_K", float("nan"))
    pctb    = latest.get("BB_PctB", float("nan"))
    sma50   = latest.get("SMA_50", float("nan"))
    sma200  = latest.get("SMA_200", float("nan"))
    atrp    = latest.get("ATR_Pct", float("nan"))
    volr    = latest.get("Vol_Ratio", float("nan"))
    signal  = latest.get("Signal", "HOLD")
    score   = latest.get("Score", 0)
    date    = str(df.index[-1].date())

    yn = lambda c: "✔ YES" if c else "✖ NO "
    golden = not np.isnan(sma50) and not np.isnan(sma200) and sma50 > sma200

    volatility = ("HIGH (>3%)" if atrp > 3 else
                  "MEDIUM (1-3%)" if atrp > 1 else "LOW (<1%)")
    vol_conv   = "HIGH CONVICTION" if volr > 1.5 else "normal"

    rsi_msg = ("OVERSOLD – potential reversal / buying opportunity" if rsi < 30 else
               "OVERBOUGHT – potential pullback / caution advised" if rsi > 70 else
               "NEUTRAL zone – no extreme pressure")

    text = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║         DETAILED SIGNAL REPORT  ·  {ticker:<10} ·  {freq:<10}              ║
╚══════════════════════════════════════════════════════════════════════════╝

  Company   : {info.get('name','N/A')}
  Sector    : {info.get('sector','N/A')}
  Industry  : {info.get('industry','N/A')}
  Date      : {date}
  Close     : {close:.4f}  {info.get('currency','')}
  Market Cap: {fmt_large(info.get('market_cap'))}

──────────────────────────────────────────────────────────────────────────
  RSI  (Relative Strength Index)
──────────────────────────────────────────────────────────────────────────
  Current RSI     : {safe(rsi,'.2f')}
  Oversold  (<30) : {yn(rsi < 30)}
  Neutral  (30-70): {yn(30 <= rsi <= 70)}
  Overbought (>70): {yn(rsi > 70)}

  → {rsi_msg}

──────────────────────────────────────────────────────────────────────────
  MACD  (Moving Average Convergence Divergence)
──────────────────────────────────────────────────────────────────────────
  MACD Line       : {safe(macd,'.6f')}
  Signal Line     : {safe(msig,'.6f')}
  Histogram       : {safe(latest.get('MACD_Hist',float('nan')),'+.6f')}
  Bullish Bias    : {yn(macd > msig)}

  → MACD {'above' if macd > msig else 'below'} Signal Line
    {'Bullish momentum' if macd > msig else 'Bearish momentum'}

──────────────────────────────────────────────────────────────────────────
  Bollinger Bands
──────────────────────────────────────────────────────────────────────────
  Upper Band      : {safe(latest.get('BB_Up',float('nan')),'.4f')}
  Middle (SMA20)  : {safe(latest.get('BB_Mid',float('nan')),'.4f')}
  Lower Band      : {safe(latest.get('BB_Lo',float('nan')),'.4f')}
  %B Position     : {safe(pctb,'.3f')}  (0 = lower band · 1 = upper band)
  Near Lower Band : {yn(pctb < 0.10)}
  Near Upper Band : {yn(pctb > 0.90)}

──────────────────────────────────────────────────────────────────────────
  Moving Averages
──────────────────────────────────────────────────────────────────────────
  Price > SMA 20  : {yn(close > latest.get('SMA_20', float('nan')))}
  Price > SMA 50  : {yn(close > sma50)}
  Price > SMA 200 : {yn(close > sma200)}
  Golden Cross    : {yn(golden)}   (SMA50 > SMA200 → long-term bullish)
  Death Cross     : {yn(not golden and not np.isnan(sma50) and not np.isnan(sma200))}

──────────────────────────────────────────────────────────────────────────
  Stochastic Oscillator
──────────────────────────────────────────────────────────────────────────
  %K              : {safe(stk,'.2f')}
  %D (SMA3 of K)  : {safe(latest.get('Stoch_D',float('nan')),'.2f')}
  Oversold  (<20) : {yn(stk < 20)}
  Overbought (>80): {yn(stk > 80)}

──────────────────────────────────────────────────────────────────────────
  Volatility & Volume
──────────────────────────────────────────────────────────────────────────
  ATR (14)        : {safe(latest.get('ATR',float('nan')),'.4f')}
  ATR % of price  : {safe(atrp,'.2f')}%
  Volatility      : {volatility}
  Volume Ratio    : {safe(volr,'.2f')}×  ({vol_conv})

──────────────────────────────────────────────────────────────────────────
  ★  COMPOSITE SIGNAL
──────────────────────────────────────────────────────────────────────────
  Score           : {score:+.0f}
  Signal          : ▶  {signal}

  Scoring Rules:
    RSI < 30             +1  (oversold – bullish)
    RSI > 70             -1  (overbought – bearish)
    MACD bullish cross   +1
    MACD bearish cross   -1
    BB %B < 0.05         +1  (near lower band)
    BB %B > 0.95         -1  (near upper band)
    Price > SMA50        +1  (uptrend)
    Price < SMA50        -1  (downtrend)
    Stoch %K < 20        +1  (oversold)
    Stoch %K > 80        -1  (overbought)

  Net Score >  +2  →  BUY
  Net Score <  -2  →  SELL
  Otherwise        →  HOLD

──────────────────────────────────────────────────────────────────────────
  ⚠  DISCLAIMER
──────────────────────────────────────────────────────────────────────────
  This analysis is for educational and informational purposes only.
  It does NOT constitute financial advice. Always conduct your own due
  diligence and consult a licensed financial advisor before investing.
  Past performance does not guarantee future results.
══════════════════════════════════════════════════════════════════════════
"""
    st.markdown(f'<div class="report-block">{text}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 – SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def build_sidebar() -> tuple[str, str, int]:
    """Render sidebar controls and return (ticker, frequency, rsi_period)."""
    with st.sidebar:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;
                    color:#00e5ff; font-size:1.1rem;
                    letter-spacing:2px; padding:12px 0 4px 0;
                    border-bottom:1px solid #30363d; margin-bottom:16px;">
            ⚡ CONTROLS
        </div>
        """, unsafe_allow_html=True)

        # Sector → stock cascade
        sector = st.selectbox("SECTOR", list(STOCK_CATALOGUE.keys()), label_visibility="visible")
        stocks = STOCK_CATALOGUE[sector]
        names  = [name for name, _ in stocks]
        choice = st.selectbox("PRESET STOCK", names)
        preset_ticker = dict(stocks)[choice]

        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;color:#768390;letter-spacing:2px;margin:16px 0 4px 0;">OR ENTER CUSTOM TICKER</div>', unsafe_allow_html=True)
        custom = st.text_input("", placeholder="e.g. AAPL, TSLA, OGDC.KA",
                               label_visibility="collapsed").strip().upper()
        ticker = custom if custom else preset_ticker

        st.markdown("---")
        freq = st.radio("TIMEFRAME", ["Daily", "Weekly", "Monthly"], horizontal=False)

        st.markdown("---")
        rsi_period = st.slider("RSI PERIOD", min_value=5, max_value=30, value=14, step=1)

        st.markdown("---")
        analyse = st.button("⚡  RUN ANALYSIS")

        # Display selected ticker
        st.markdown(f"""
        <div style="font-family:'Share Tech Mono',monospace;margin-top:12px;
                    padding:10px 14px;background:#161b22;border:1px solid #30363d;
                    border-radius:4px;font-size:0.8rem;">
            <span style="color:#768390">TICKER</span><br>
            <span style="color:#00e5ff;font-size:1.1rem;">{ticker}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                    color:#4a5568;margin-top:32px;line-height:1.8;">
            Data: Yahoo Finance<br>
            For educational use only.<br>
            Not financial advice.
        </div>
        """, unsafe_allow_html=True)

    return ticker, freq, rsi_period, analyse


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 – MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Header
    st.markdown("""
    <div class="top-bar">
        <div>
            <h1>📈 STOCK ANALYZER PRO</h1>
            <p>Technical Analysis Dashboard · RSI · MACD · Bollinger Bands · Signals</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    ticker, freq, rsi_period, analyse = build_sidebar()

    # ── Session state: persist last result ───────────────────────────────────
    if "df_enriched" not in st.session_state:
        st.session_state.df_enriched = None
        st.session_state.info        = None
        st.session_state.ticker      = None
        st.session_state.freq        = None

    if analyse or (st.session_state.ticker != ticker or
                   st.session_state.freq   != freq):
        with st.spinner(f"Fetching {ticker} · {freq} data …"):
            try:
                raw  = fetch_data(ticker, freq)
                info = fetch_info(ticker)
                df   = compute_indicators(raw, rsi_period=rsi_period)
                st.session_state.df_enriched = df
                st.session_state.info        = info
                st.session_state.ticker      = ticker
                st.session_state.freq        = freq
            except Exception as e:
                st.error(f"⚠ {e}")
                return

    df   = st.session_state.df_enriched
    info = st.session_state.info

    if df is None:
        st.markdown("""
        <div style="text-align:center;padding:80px 0;font-family:'Share Tech Mono',monospace;
                    color:#768390;font-size:0.9rem;letter-spacing:2px;">
            SELECT A STOCK AND CLICK  ⚡ RUN ANALYSIS
        </div>
        """, unsafe_allow_html=True)
        return

    latest = df.iloc[-1].to_dict()

    # ── Metric cards row ─────────────────────────────────────────────────────
    render_metric_cards(latest, info)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "  📊  CHART  ",
        "  🔢  INDICATORS  ",
        "  📋  SIGNAL REPORT  ",
        "  📉  HISTORICAL DATA  ",
    ])

    with tab1:
        fig = build_chart(df, ticker, freq)
        st.plotly_chart(fig, use_container_width=True, config={
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "displaylogo": False,
        })

    with tab2:
        col_sig, col_ind = st.columns([1, 3], gap="large")
        with col_sig:
            render_signal_box(latest)

            # Company info card
            st.markdown('<div class="section-header">COMPANY INFO</div>', unsafe_allow_html=True)
            items = [
                ("NAME",       info.get("name","N/A")),
                ("SECTOR",     info.get("sector","N/A")),
                ("INDUSTRY",   info.get("industry","N/A")),
                ("MARKET CAP", fmt_large(info.get("market_cap"))),
                ("P/E RATIO",  safe(info.get("pe_ratio"), ".1f")),
                ("52W HIGH",   safe(info.get("52w_high"), ".2f")),
                ("52W LOW",    safe(info.get("52w_low"), ".2f")),
                ("CURRENCY",   info.get("currency","USD")),
            ]
            rows_html = "".join(
                f'<div style="display:flex;justify-content:space-between;padding:5px 0;'
                f'border-bottom:1px solid #21262d;font-size:0.75rem;">'
                f'<span style="color:#768390;font-family:\'Share Tech Mono\',monospace;">{k}</span>'
                f'<span style="color:#cdd9e5;font-family:\'Share Tech Mono\',monospace;">{v}</span>'
                f'</div>'
                for k, v in items
            )
            st.markdown(f'<div style="background:#0d1117;border:1px solid #30363d;'
                        f'border-radius:6px;padding:14px 18px;">{rows_html}</div>',
                        unsafe_allow_html=True)

        with col_ind:
            st.markdown('<div class="section-header">ALL INDICATORS  –  LATEST VALUES</div>',
                        unsafe_allow_html=True)
            render_indicator_grid(latest)

    with tab3:
        render_report(ticker, freq, info, latest, df)

    with tab4:
        st.markdown('<div class="section-header">HISTORICAL OHLCV  +  INDICATORS</div>',
                    unsafe_allow_html=True)
        display_cols = [
            "Open","High","Low","Close","Volume",
            "RSI","MACD","MACD_Sig","BB_Up","BB_Lo","BB_PctB",
            "SMA_20","SMA_50","SMA_200","Stoch_K","ATR_Pct","Vol_Ratio","Signal"
        ]
        show_df = df[[c for c in display_cols if c in df.columns]].copy()
        show_df.index = show_df.index.date
        show_df = show_df.iloc[::-1].round(4)   # newest first

        def color_signal(val):
            if val == "BUY":  return "color: #00e676; font-weight: bold"
            if val == "SELL": return "color: #ff1744; font-weight: bold"
            return "color: #ffd740"

        #
        styled = (
            show_df.style
            .map(color_signal, subset=["Signal"])  # ✅ FIXED HERE
            .format(precision=4)
            .set_properties(**{
                "background-color": "#0d1117",
                "color": "#cdd9e5",
                "border-color": "#30363d",
                "font-family": "'Share Tech Mono', monospace",
                "font-size": "0.75rem",
            })
            .set_table_styles([{
                "selector": "th",
                "props": [
                    ("background-color", "#161b22"),
                    ("color", "#00e5ff"),
                    ("font-family", "'Share Tech Mono', monospace"),
                    ("font-size", "0.7rem"),
                    ("letter-spacing", "1px"),
                ],
            }])
        )





        st.dataframe(styled, use_container_width=True, height=500)

        # Download CSV
        csv = show_df.to_csv()
        st.download_button(
            label="⬇  DOWNLOAD CSV",
            data=csv,
            file_name=f"{ticker}_{freq}_analysis.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
