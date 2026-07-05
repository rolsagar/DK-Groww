"""
DK Groww — RSI + MACD Technical Dashboard
A Streamlit dashboard that replicates the classic RSI-MACD stock analysis
layout, tracking a fixed watchlist of NSE-listed stocks/ETFs with the
option to type in any custom ticker.
"""

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="DK Groww",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Watchlist — name shown to the user -> Yahoo Finance / NSE ticker
# --------------------------------------------------------------------------
WATCHLIST = {
    "GAIL (INDIA) LTD": "GAIL.NS",
    "HDFC BANK LTD": "HDFCBANK.NS",
    "ICICI BANK LTD.": "ICICIBANK.NS",
    "INDIAN OIL CORP LTD": "IOC.NS",
    "INTERGLOBE AVIATION LTD": "INDIGO.NS",
    "ITC LTD": "ITC.NS",
    "LARSEN & TOUBRO LTD.": "LT.NS",
    "MOTILAL OS NASDAQ100 ETF": "MON100.NS",
    "NIP IND ETF GOLD BEES": "GOLDBEES.NS",
    "RELIANCE INDUSTRIES LTD": "RELIANCE.NS",
    "SBIAMC - SBISILVER": "SBISILVER.NS",
    "TATA CONSUMER PRODUCT LTD": "TATACONSUM.NS",
    "TATAAML-TATAGOLD": "TATAGOLD.NS",
    "TATAAML-TATSILV": "TATSILV.NS",
    "TRENT LTD": "TRENT.NS",
}

PERIOD_OPTIONS = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
}

# --------------------------------------------------------------------------
# Indicator calculations
# --------------------------------------------------------------------------
def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def compute_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


@st.cache_data(ttl=900)
def load_data(ticker: str, period: str) -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna()
    return df


def get_signal(rsi_val: float, macd_val: float, signal_val: float, rsi_buy: int, rsi_sell: int) -> str:
    macd_bullish = macd_val > signal_val
    if rsi_val < rsi_buy and macd_bullish:
        return "BUY"
    if rsi_val > rsi_sell and not macd_bullish:
        return "SELL"
    return "HOLD"


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
st.sidebar.title("📈 DK Groww")
st.sidebar.caption("RSI + MACD Technical Dashboard")

st.sidebar.markdown("### Select Stock")
pick_mode = st.sidebar.radio("Pick from list or type your own", ["Watchlist", "Custom ticker"], horizontal=True)

if pick_mode == "Watchlist":
    display_name = st.sidebar.selectbox("Stock / ETF", list(WATCHLIST.keys()))
    ticker = WATCHLIST[display_name]
else:
    display_name = st.sidebar.text_input("Enter NSE symbol (e.g. WIPRO)", value="WIPRO").strip().upper()
    ticker = f"{display_name}.NS" if display_name and not display_name.endswith((".NS", ".BO")) else display_name

st.sidebar.markdown("### Time Range")
period_label = st.sidebar.selectbox("Period", list(PERIOD_OPTIONS.keys()), index=3)
period = PERIOD_OPTIONS[period_label]

st.sidebar.markdown("### RSI Settings")
rsi_period = st.sidebar.slider("RSI Period", 5, 30, 14)
rsi_buy_level = st.sidebar.slider("Oversold (Buy below)", 10, 40, 30)
rsi_sell_level = st.sidebar.slider("Overbought (Sell above)", 60, 90, 70)

st.sidebar.markdown("### MACD Settings")
macd_fast = st.sidebar.slider("Fast EMA", 5, 20, 12)
macd_slow = st.sidebar.slider("Slow EMA", 15, 40, 26)
macd_signal_span = st.sidebar.slider("Signal EMA", 5, 15, 9)

st.sidebar.markdown("---")
st.sidebar.caption("Data via Yahoo Finance. For educational purposes only — not investment advice.")

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
st.title("📈 DK Groww")
st.caption(f"Technical analysis for **{display_name}** ({ticker})")

if not ticker:
    st.warning("Please select or enter a stock ticker.")
    st.stop()

try:
    data = load_data(ticker, period)
except Exception as e:
    st.error(f"Could not fetch data for {ticker}: {e}")
    st.stop()

if data.empty or len(data) < 30:
    st.error(f"No sufficient data found for '{ticker}'. Check the symbol and try again.")
    st.stop()

close = data["Close"]
data["RSI"] = compute_rsi(close, rsi_period)
data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = compute_macd(
    close, macd_fast, macd_slow, macd_signal_span
)

latest = data.iloc[-1]
prev = data.iloc[-2]
price_change = latest["Close"] - prev["Close"]
price_change_pct = (price_change / prev["Close"]) * 100
signal = get_signal(latest["RSI"], latest["MACD"], latest["MACD_Signal"], rsi_buy_level, rsi_sell_level)

# ---- Top metrics row ----
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Last Price", f"₹{latest['Close']:.2f}", f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
col2.metric("52W High", f"₹{data['High'].max():.2f}")
col3.metric("52W Low", f"₹{data['Low'].min():.2f}")
col4.metric("RSI", f"{latest['RSI']:.1f}")

signal_colors = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}
col5.metric("Signal", f"{signal_colors[signal]} {signal}")

st.markdown("---")

# ---- Price chart with candlesticks ----
fig = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.04,
    row_heights=[0.5, 0.25, 0.25],
    subplot_titles=("Price", "RSI", "MACD"),
)

fig.add_trace(
    go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Price",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
    ),
    row=1,
    col=1,
)

ema20 = close.ewm(span=20, adjust=False).mean()
ema50 = close.ewm(span=50, adjust=False).mean()
fig.add_trace(go.Scatter(x=data.index, y=ema20, name="EMA 20", line=dict(color="#f0a500", width=1)), row=1, col=1)
fig.add_trace(go.Scatter(x=data.index, y=ema50, name="EMA 50", line=dict(color="#7e57c2", width=1)), row=1, col=1)

# RSI
fig.add_trace(go.Scatter(x=data.index, y=data["RSI"], name="RSI", line=dict(color="#2196f3", width=1.5)), row=2, col=1)
fig.add_hline(y=rsi_sell_level, line_dash="dash", line_color="#ef5350", row=2, col=1)
fig.add_hline(y=rsi_buy_level, line_dash="dash", line_color="#26a69a", row=2, col=1)
fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)

# MACD
colors = ["#26a69a" if v >= 0 else "#ef5350" for v in data["MACD_Hist"]]
fig.add_trace(go.Bar(x=data.index, y=data["MACD_Hist"], name="Histogram", marker_color=colors), row=3, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data["MACD"], name="MACD", line=dict(color="#2196f3", width=1.5)), row=3, col=1)
fig.add_trace(go.Scatter(x=data.index, y=data["MACD_Signal"], name="Signal", line=dict(color="#f0a500", width=1.5)), row=3, col=1)

fig.update_layout(
    height=850,
    showlegend=True,
    xaxis_rangeslider_visible=False,
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

st.plotly_chart(fig, use_container_width=True)

# ---- Signal explanation ----
with st.expander("How is the signal calculated?"):
    st.markdown(
        f"""
        - **RSI({rsi_period})** below **{rsi_buy_level}** = oversold; above **{rsi_sell_level}** = overbought.
        - **MACD** bullish when the MACD line is above its signal line, bearish when below.
        - **BUY** → RSI oversold **and** MACD bullish.
        - **SELL** → RSI overbought **and** MACD bearish.
        - Otherwise → **HOLD**.

        Current readings: RSI = **{latest['RSI']:.1f}**, MACD = **{latest['MACD']:.2f}**, Signal = **{latest['MACD_Signal']:.2f}**.
        """
    )

# ---- Raw data ----
with st.expander("View raw data"):
    st.dataframe(data.tail(100).sort_index(ascending=False), use_container_width=True)

st.markdown("---")
st.caption("DK Groww · Data sourced from Yahoo Finance via yfinance · Not financial advice.")
