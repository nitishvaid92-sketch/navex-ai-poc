 import streamlit as st
import yfinance as yf
from groq import Groq

st.set_page_config(
    page_title="NAVEX AI Intelligence V0.1", 
    page_icon="📈", 
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

st.title("NAVEX AI Intelligence — Live EUR/USD PoC")
st.caption("Pre-seed Proof of Concept | Live Data Feed → Quant Engine → AI Reasoning")

@st.cache_data(ttl=30)
def fetch_market_data():
    eurusd = yf.Ticker("EURUSD=X")
    hist = eurusd.history(period="5d", interval="1h")
    current_price = hist['Close'].iloc[-1]
    prev_close = hist['Close'].iloc[-2]
    price_change = current_price - prev_close
    
    sma_20 = hist['Close'].rolling(20).mean().iloc[-1]
    volatility = hist['High'].iloc[-1] - hist['Low'].iloc[-1]
    
    return current_price, price_change, sma_20, volatility, hist

try:
    price, change, sma20, vol, df = fetch_market_data()
except Exception as e:
    st.error(f"Error fetching live data: {e}")
    st.stop()

client = Groq(api_key="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")

def get_ai_intelligence(price, sma20, vol):
    prompt = f"""
    You are NAVEX AI, an institutional quantitative market analyst. 
    Current EUR/USD Data:
    - Price: {price:.5f}
    - 20 SMA: {sma20:.5f}
    - Recent Candle Volatility: {vol:.5f}
    
    Provide a strict evaluation following this exact structure:
    Market Bias: [Bullish/Bearish/Neutral]
    Confidence: [e.g., 78%]
    Market Regime: [Trending/Ranging/Breakout]
    Liquidity: [e.g., Sell-side sweep detected]
    Volatility: [Low/Moderate/High]
    Setup Quality: [e.g., 8.1/10]
    Risk: [Low/Medium/High]
    NAVEX AI Summary: [A concise 2-sentence institutional observation explaining the reasoning.]
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices.message.content

ai_output = get_ai_intelligence(price, sma20, vol)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Live Market Feed")
    st.metric("EUR/USD Spot Price", f"{price:.5f}", f"{change:+.5f}")
    st.line_chart(df['Close'])

with col2:
    st.subheader("NAVEX AI Intelligence Layer")
    st.info(ai_output)

if st.button("Refresh Intelligence Stream"):
    st.rerun()
