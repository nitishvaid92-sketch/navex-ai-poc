import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from groq import Groq
import pandas as pd

st.set_page_config(
    page_title="NAVEX AI Intelligence V0 — Pre-Seed PoC",
    page_icon="📈",
    layout="wide"
)

# Custom Fintech Styling (Warm White, Deep Navy, Charcoal, Gold Accents)
st.markdown("""
    <style>
    .stApp {
        background-color: #fcfbf9;
        color: #2d3748;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h1, h2, h3, h4 {
        color: #0a192f !important;
        font-weight: 700;
    }
    .disclaimer-box {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        padding: 12px 18px;
        border-radius: 6px;
        color: #92400e;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .ai-panel {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #0a192f;
        padding: 20px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# V0 Disclaimer Header
st.markdown("""
<div class="disclaimer-box">
    <strong>NAVEX AI Intelligence V0 — Pre-Seed Technical Proof of Concept</strong><br>
    Demonstrating the core NAVEX intelligence pipeline using live EUR/USD market data. This is an early technical proof-of-concept, not a production trading system or automated execution platform.
</div>
""", unsafe_allow_html=True)

st.title("NAVEX AI Intelligence — Live EUR/USD PoC")
st.caption("Pre-seed Proof of Concept | Live Data Feed → Quant Engine → Institutional AI Reasoning")

@st.cache_data(ttl=60)
def fetch_market_data():
    # Fetching 7 days of 1-hour candles to ensure 100+ clean data points
    eurusd = yf.Ticker("EURUSD=X")
    df = eurusd.history(period="7d", interval="1h")
    if df.empty:
        df = eurusd.history(period="5d", interval="1h")
    
    current_price = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    price_change = current_price - prev_close
    pct_change = (price_change / prev_close) * 100
    
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['Volatility'] = df['High'] - df['Low']
    
    return current_price, price_change, pct_change, df

try:
    price, change, pct_change, df = fetch_market_data()
    sma20 = df['SMA_20'].iloc[-1]
    vol = df['Volatility'].iloc[-1]
except Exception as e:
    st.error(f"Error fetching live data feed: {e}")
    st.stop()

client = Groq(api_key="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")

def get_ai_intelligence(price, sma20, vol, change):
    prompt = f"""
    You are NAVEX AI, an institutional quantitative market analyst. 
    Current EUR/USD Market State:
    - Spot Price: {price:.5f}
    - 20-period SMA: {sma20:.5f}
    - Recent Change: {change:+.5f}
    - Candle Volatility Range: {vol:.5f}
    
    Provide a rigorous institutional evaluation following this exact strict structure:
    Market Bias: [Bullish/Bearish/Neutral]
    Confidence: [e.g., 62%]
    Market Regime: [Trending/Ranging/Breakout/High-volatility]
    Liquidity: [Low/Moderate/High - explain briefly]
    Volatility: [Low/Moderate/High]
    Setup Quality: [Score out of 10, e.g., 6.5/10]
    Risk: [Low/Medium/High - explain why]
    
    NAVEX AI Summary & Reasoning:
    [Write a comprehensive 3-4 sentence institutional-grade market observation explaining what is happening, why it is happening based on price behavior and moving averages, and what market conditions would invalidate or change the assessment. Avoid generic ChatGPT fluff; sound like a professional quantitative analyst.]
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

ai_output = get_ai_intelligence(price, sma20, vol, change)

# Layout: Two columns (Professional Chart on left, AI Intelligence on right)
col_chart, col_ai = st.columns([1.2, 1])

with col_chart:
    st.subheader("Professional Market Feed & Candlestick Chart")
    st.metric("EUR/USD Spot Price", f"{price:.5f}", f"{change:+.5f} ({pct_change:+.2f}%)")
    
    # Plotly Candlestick Chart with 100+ candles
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="EUR/USD"
    )])
    
    # Add 20 SMA line
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['SMA_20'], 
        mode='lines', 
        name='20 SMA', 
        line=dict(color='#c5a059', width=1.5)
    ))
    
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=10, b=10),
        height=420,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Displaying last {len(df)} intraday hourly candles with 20 SMA overlay.")

with col_ai:
    st.subheader("NAVEX AI Intelligence Layer")
    st.markdown(f"""
    <div class="ai-panel">
        {ai_output.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("Refresh Market Intelligence Stream", use_container_width=True):
        st.rerun()

st.markdown("---")

# Architecture Section
with st.expander("🔍 View NAVEX Technical Architecture Pipeline", expanded=False):
    st.markdown("""
    ### Core Technical Pipeline
    ```text
    LIVE EUR/USD DATA (yfinance feed)
           ↓
    MARKET DATA PROCESSING (OHLCV normalization & technical feature extraction)
           ↓
    QUANT / MARKET ANALYSIS (Moving averages, volatility, regime detection)
           ↓
    NAVEX AI INTELLIGENCE ENGINE (Institutional Llama-3.1 quantization & evaluation)
           ↓
    MARKET REGIME + BIAS + RISK + SETUP QUALITY
           ↓
    AI REASONING (Human-readable institutional market commentary)
    ```
    *Note: This architecture demonstrates the pre-seed technical foundation. Brokerage execution, automated trading, and portfolio management are intentionally excluded from this V0 prototype.*
    """)

# Investor Objective Note
st.markdown("""
### 💡 Investor Context & Objective
* **Current Stage:** Pre-MVP • Pre-Revenue • Pre-Seed
* **Purpose:** This technical proof-of-concept demonstrates that NAVEX can ingest live market information, run quantitative analysis, and produce rigorous, institutional-grade market intelligence.
* **Use of Pre-Seed Capital:** To transition this validated technical foundation into the full-scale NAVEX platform.
""")
