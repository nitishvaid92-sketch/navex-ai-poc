import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from groq import Groq
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="NAVEX AI Intelligence V0 — Pre-Seed PoC",
    page_icon="📈",
    layout="wide"
)

# Custom Fintech Institutional Styling
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
        padding: 14px 18px;
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
    .trader-takeaway {
        background-color: #f7fafc;
        border: 1px solid #cbd5e0;
        border-left: 4px solid #4a5568;
        padding: 15px;
        border-radius: 6px;
        margin-top: 15px;
        font-size: 14px;
        color: #2d3748;
    }
    .signal-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .signal-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #718096;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .signal-value {
        font-size: 14px;
        color: #0a192f;
        font-weight: 700;
    }
    .platform-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 6px;
        height: 100%;
    }
    .validation-metric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 6px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 1. TOP POSITIONING & STAGE DISCLAIMER
st.markdown("""
<div class="disclaimer-box">
    <strong>NAVEX AI Intelligence V0 — Pre-MVP / Pre-Revenue Proof of Concept</strong><br>
    This demonstration validates the initial NAVEX intelligence workflow. It is not a production trading system and does not represent historical trading performance.
</div>
""", unsafe_allow_html=True)

col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("EUR/USD — Live Market Intelligence")
    st.caption("Pre-seed Proof of Concept | Live Data Feed → Quantitative Engine → AI Reasoning Layer")
with col_head2:
    st.markdown("<br>", unsafe_allow_html=True)
    current_time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    st.markdown(f"🟢 **LIVE FEED ACTIVE**  \n*Last Updated: {current_time_str}*")

# 2. LIVE MARKET DATA INGESTION
@st.cache_data(ttl=30)
def fetch_market_data():
    eurusd = yf.Ticker("EURUSD=X")
    df = eurusd.history(period="7d", interval="1h")
    if df.empty or len(df) < 50:
        df = eurusd.history(period="5d", interval="1h")
    
    current_price = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    price_change = current_price - prev_close
    pct_change = (price_change / prev_close) * 100
    
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['Volatility'] = df['High'] - df['Low']
    
    recent_high = df['High'].tail(50).max()
    recent_low = df['Low'].tail(50).min()
    
    return current_price, price_change, pct_change, recent_high, recent_low, df

try:
    price, change, pct_change, rec_high, rec_low, df = fetch_market_data()
    sma20 = df['SMA_20'].iloc[-1]
    vol = df['Volatility'].iloc[-1]
except Exception as e:
    st.error(f"Error fetching live data feed: {e}")
    st.stop()

# 3 & 4. NAVEX AI INTELLIGENCE PANEL & REASONING
client = Groq(api_key="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")

def get_ai_intelligence(price, sma20, vol, change, rec_high, rec_low):
    prompt = f"""
    You are NAVEX AI, a quantitative market analysis assistant. 
    Current EUR/USD Market State:
    - Spot Price: {price:.5f}
    - 20-period SMA: {sma20:.5f}
    - Recent Change: {change:+.5f}
    - Recent 50-candle High: {rec_high:.5f}
    - Recent 50-candle Low: {rec_low:.5f}
    - Candle Volatility Range: {vol:.5f}
    
    Provide a rigorous evaluation based strictly on these live numbers. Format your response clearly using these exact headings:
    MARKET BIAS: [Bullish / Bearish / Neutral]
    AI ASSESSMENT CONFIDENCE: [e.g., 62%]
    MARKET REGIME: [Trending / Ranging / Breakout / High-volatility]
    MARKET STRUCTURE: [e.g., No confirmed directional break / Higher highs / Lower lows]
    LIQUIDITY: [Low / Moderate / High]
    VOLATILITY: [Low / Moderate / High]
    MOMENTUM: [Weak / Neutral / Strong]
    SETUP QUALITY: [Score out of 10, e.g., 6.8 / 10]
    RISK: [Low / Low–Moderate / Moderate / High]
    
    NAVEX AI Reasoning:
    [Provide a concise 3-4 sentence institutional-grade explanation of what the system is seeing, why it is happening based on price behavior and moving averages, and what conditions would change the assessment.]
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

ai_output = get_ai_intelligence(price, sma20, vol, change, rec_high, rec_low)

col_chart, col_ai = st.columns([1.3, 1])

with col_chart:
    st.subheader("Price Action & Technical Overlay")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Spot Price", f"{price:.5f}", f"{change:+.5f} ({pct_change:+.2f}%)")
    with metric_col2:
        st.metric("50-Candle High", f"{rec_high:.5f}")
    with metric_col3:
        st.metric("50-Candle Low", f"{rec_low:.5f}")
    
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="EUR/USD Candles",
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    )])
    
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['SMA_20'], 
        mode='lines', 
        name='20 SMA', 
        line=dict(color='#c5a059', width=2)
    ))
    
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=10, b=10),
        height=450,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Displaying {len(df)} intraday hourly candles with 20 SMA overlay and dynamic price scaling.")

with col_ai:
    st.subheader("NAVEX AI Intelligence Panel")
    st.markdown(f"""
    <div class="ai-panel">
        {ai_output.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)
    
    # 5. NAVEX TRADER TAKEAWAY
    st.markdown("""
    <div class="trader-takeaway">
        <strong>NAVEX Trader Takeaway</strong><br>
        No high-conviction setup detected. NAVEX recommends waiting for confirmation rather than forcing a trade.<br><br>
        <strong>Bias:</strong> Neutral &nbsp;|&nbsp; <strong>Action:</strong> Wait &nbsp;|&nbsp; <strong>Trigger:</strong> Confirmed directional break + momentum expansion &nbsp;|&nbsp; <strong>Risk:</strong> Low–Moderate
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("Refresh Market Intelligence Stream", use_container_width=True):
        st.rerun()

st.markdown("---")

# 6. INTELLIGENCE SIGNALS
st.subheader("What NAVEX Is Seeing — Intelligence Signals")
sig_col1, sig_col2, sig_col3, sig_col4, sig_col5 = st.columns(5)

with sig_col1:
    st.markdown("""
    <div class="signal-card">
        <div class="signal-title">Market Structure</div>
        <div class="signal-value">Range / Compression</div>
    </div>
    """, unsafe_allow_html=True)
with sig_col2:
    st.markdown("""
    <div class="signal-card">
        <div class="signal-title">Liquidity</div>
        <div class="signal-value">Moderate Level</div>
    </div>
    """, unsafe_allow_html=True)
with sig_col3:
    st.markdown("""
    <div class="signal-card">
        <div class="signal-title">Volatility</div>
        <div class="signal-value">Compressed</div>
    </div>
    """, unsafe_allow_html=True)
with sig_col4:
    st.markdown("""
    <div class="signal-card">
        <div class="signal-title">Momentum</div>
        <div class="signal-value">Weak / Neutral</div>
    </div>
    """, unsafe_allow_html=True)
with sig_col5:
    st.markdown("""
    <div class="signal-card">
        <div class="signal-title">Risk Environment</div>
        <div class="signal-value" style="color: #2b6cb0;">Low–Moderate</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("""
<div style="font-size: 13px; color: #4a5568; background-color: #fff; padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 4px;">
    <strong>Intelligence Inputs Considered:</strong> Price Action | Market Structure | Liquidity | Volatility | Momentum<br>
    <strong>Future Intelligence Inputs:</strong> Macro | News | Sentiment | Trader Behaviour
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 7. TECHNICAL ARCHITECTURE & SCOPE BOUNDARY
with st.expander("🔍 Core NAVEX Technical Pipeline & Architecture", expanded=False):
    st.markdown("""
    ```text
    LIVE EUR/USD MARKET DATA
           ↓
    DATA NORMALIZATION & FEATURE EXTRACTION
           ↓
    QUANTITATIVE MARKET ANALYSIS
           ↓
    NAVEX AI INTELLIGENCE ENGINE
           ↓
    MARKET STRUCTURE + LIQUIDITY + VOLATILITY + MOMENTUM
           ↓
    REGIME + BIAS + RISK + SETUP QUALITY
           ↓
    AI REASONING & MARKET INTELLIGENCE
    ```
    
    <strong>Scope Boundary:</strong>  
    V0 demonstrates the core intelligence pipeline. Brokerage execution, portfolio management, automated trading and other production capabilities are intentionally outside the scope of this proof-of-concept.
    """, unsafe_allow_html=True)

st.markdown("---")

# 8. INVESTOR CONTEXT & OBJECTIVE
st.subheader("Investor Context & Objective")
st.markdown("""
<div style="background-color: #ffffff; border: 1px solid #e2e8f0; padding: 18px; border-radius: 6px; font-size: 14px; color: #2d3748;">
    <strong>Current Stage:</strong> Pre-MVP • Pre-Revenue • Pre-Seed<br><br>
    <strong>Purpose:</strong> This proof-of-concept demonstrates the initial NAVEX intelligence workflow using live market information, quantitative analysis and an AI reasoning layer.<br><br>
    <strong>Pre-Seed Objective:</strong> Use pre-seed capital to expand, validate and productize this intelligence foundation into the NAVEX AI-native trading platform.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# 9. EARLY TRADER VALIDATION
st.subheader("Early Trader Validation")
val_col1, val_col2, val_col3 = st.columns(3)

with val_col1:
    st.markdown("""
    <div class="validation-metric">
        <div class="signal-title">Traders Contacted</div>
        <div style="font-size: 28px; font-weight: 700; color: #0a192f; margin-top: 5px;">173</div>
    </div>
    """, unsafe_allow_html=True)
with val_col2:
    st.markdown("""
    <div class="validation-metric">
        <div class="signal-title">Expressed Interest in Beta</div>
        <div style="font-size: 28px; font-weight: 700; color: #0a192f; margin-top: 5px;">158</div>
    </div>
    """, unsafe_allow_html=True)
with val_col3:
    st.markdown("""
    <div class="validation-metric">
        <div class="signal-title">Average Reported Trading Capital</div>
        <div style="font-size: 28px; font-weight: 700; color: #0a192f; margin-top: 5px;">$3,000</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='font-size: 13px; color: #718096; margin-top: 8px;'><em>Outreach is ongoing as NAVEX continues building its early beta cohort.</em></div>", unsafe_allow_html=True)

st.markdown("---")

# 10. FROM V0 TO NAVEX PLATFORM
st.subheader("From V0 to NAVEX Platform")
plat_col1, plat_col2, plat_col3 = st.columns(3)

with plat_col1:
    st.markdown("""
    <div class="platform-card">
        <h4 style="color: #0a192f; margin-top:0;">TODAY — AI INTELLIGENCE V0</h4>
        <ul style="padding-left: 18px; font-size: 14px; color: #4a5568;">
            <li>Live market data ingestion</li>
            <li>Quantitative market analysis</li>
            <li>AI reasoning engine</li>
            <li>Structured market intelligence</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with plat_col2:
    st.markdown("""
    <div class="platform-card">
        <h4 style="color: #0a192f; margin-top:0;">PRE-SEED BUILD</h4>
        <ul style="padding-left: 18px; font-size: 14px; color: #4a5568;">
            <li>Multi-asset intelligence (FX, Gold, Indices, Equities, Crypto)</li>
            <li>Deeper market-structure and liquidity intelligence</li>
            <li>Macro and news integration</li>
            <li>Sentiment and behavioural signals</li>
            <li>Historical validation / backtesting</li>
            <li>Model evaluation & trader beta feedback</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with plat_col3:
    st.markdown("""
    <div class="platform-card">
        <h4 style="color: #0a192f; margin-top:0;">NAVEX PLATFORM</h4>
        <ul style="padding-left: 18px; font-size: 14px; color: #4a5568;">
            <li>AI-native trading intelligence</li>
            <li>Advanced charting & trade planning</li>
            <li>Trading journal & portfolio risk intelligence</li>
            <li>Broker integration & execution infrastructure</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 11. WHAT PRE-SEED CAPITAL BUILDS
st.subheader("What Pre-Seed Capital Builds")
build_col1, build_col2, build_col3, build_col4 = st.columns(4)

with build_col1:
    st.markdown("""
    <div class="platform-card">
        <h4 style="color: #0a192f; margin-top:0; font-size: 15px;">1. EXPAND</h4>
        <p style="font-size: 13px; color: #4a5568;">Expand the intelligence engine from a single-asset proof-of-concept to multi-asset market intelligence.</p>
    </div>
    """, unsafe_allow_html=True)
with build_col2:
    st.markdown("""
    <div class="platform-card">
        <h4 style="color: #0a192f; margin-top:0; font-size: 15px;">2. VALIDATE</h4>
        <p style="font-size: 13px; color: #4a5568;">Validate intelligence through historical testing, model evaluation and structured beta feedback loops.</p>
    </div>
    """, unsafe_allow_html=True)
with build_col3:
    st.markdown("""
    <div class="platform-card">
        <h4 style="color: #0a192f; margin-top:0; font-size: 15px;">3. PRODUCTIZE</h4>
        <p style="font-size: 13px; color: #4a5568;">Turn the validated intelligence layer into the core of the NAVEX trading platform.</p>
    </div>
    """, unsafe_allow_html=True)
with build_col4:
    st.markdown("""
    <div class="platform-card">
        <h4 style="color: #0a192f; margin-top:0; font-size: 15px;">4. SCALE</h4>
        <p style="font-size: 13px; color: #4a5568;">Prepare infrastructure, integrations and product experience required for broader trader adoption.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 12. COMMERCIAL POTENTIAL / WHY THIS MATTERS
st.subheader("Why This Matters")
st.markdown("""
<div style="background-color: #ebf8ff; border-left: 4px solid #3182ce; padding: 16px 20px; border-radius: 4px; color: #2b6cb0; font-size: 15px;">
    <strong>Commercial & Strategic Potential:</strong><br>
    NAVEX is demonstrating the intelligence layer today. The pre-seed objective is to turn this technical foundation into a complete AI-native trading platform that helps traders make better-informed decisions while creating multiple potential revenue streams across intelligence subscriptions, trading infrastructure and brokerage services.
</div>
""", unsafe_allow_html=True)
