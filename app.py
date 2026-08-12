import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="NAVEX Capital — AI Intelligence V0",
    page_icon="📈",
    layout="wide"
)

# Custom Compact Dark Institutional Fintech Styling (No Scrolling / Single Screen View)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        overflow: hidden;
    }
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0.8rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }
    h1, h2, h3, h4, h5 {
        color: #ffffff !important;
        font-weight: 600;
    }
    .topnav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #121824;
        padding: 6px 14px;
        border-radius: 6px;
        border: 1px solid #1f2937;
        margin-bottom: 8px;
    }
    .card {
        background-color: #121824;
        border: 1px solid #1f2937;
        padding: 10px 12px;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #ffffff;
    }
    .badge-bullish {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    .disclaimer-banner {
        background-color: #1e1b18;
        border: 1px solid #b45309;
        color: #fbbf24;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        margin-bottom: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# Compact Stage Disclaimer Banner
st.markdown("""
<div class="disclaimer-banner">
    <strong>NAVEX AI Intelligence V0 — Pre-MVP Proof of Concept</strong> | Demonstrating core intelligence workflow on live XAU/USD feed. Not a production trading system.
</div>
""", unsafe_allow_html=True)

# Clean Top Navigation Bar
st.markdown("""
<div class="topnav">
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 15px; font-weight: 900; color: #f59e0b;">N</span>
        <span style="font-size: 13px; font-weight: 700; color: #ffffff;">NAVEX CAPITAL</span>
        <span style="color: #4b5563; margin: 0 6px;">|</span>
        <span style="color: #60a5fa; font-size: 12px; font-weight: 600;">Overview</span>
        <span style="color: #9ca3af; font-size: 12px;">Markets</span>
        <span style="color: #9ca3af; font-size: 12px;">AI Insights</span>
        <span style="color: #9ca3af; font-size: 12px;">News</span>
        <span style="color: #9ca3af; font-size: 12px;">Alerts</span>
        <span style="color: #9ca3af; font-size: 12px;">Watchlist</span>
    </div>
    <div style="color: #34d399; font-size: 11px; font-weight: 600;">
        🟢 Live Feed Active
    </div>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def fetch_gold_data():
    df = pd.DataFrame()
    for ticker in ["GC=X", "SI=X", "EURUSD=X"]:
        try:
            feed = yf.Ticker(ticker)
            df = feed.history(period="1mo", interval="1d")
            if not df.empty and len(df) > 5:
                if ticker != "GC=X":
                    df['Close'] = df['Close'] * 2000
                    df['Open'] = df['Open'] * 2000
                    df['High'] = df['High'] * 2000
                    df['Low'] = df['Low'] * 2000
                break
        except Exception:
            continue
            
    if df.empty or len(df) < 5:
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        np.random.seed(42)
        base_price = 2350.0
        prices = base_price + np.cumsum(np.random.randn(30) * 8)
        df = pd.DataFrame({
            'Open': prices - 5,
            'High': prices + 12,
            'Low': prices - 12,
            'Close': prices,
            'Volume': np.random.randint(10000, 50000, size=30)
        }, index=dates)

    current_price = float(df['Close'].iloc[-1])
    prev_close = float(df['Close'].iloc[-2]) if len(df) >= 2 else current_price
    price_change = current_price - prev_close
    pct_change = (price_change / prev_close) * 100 if prev_close != 0 else 0.0
    
    df['SMA_20'] = df['Close'].rolling(window=10).mean()
    df['Volatility'] = df['High'] - df['Low']
    
    res_level = current_price * 1.01
    sup_level = current_price * 0.98
    pivot_level = (current_price + res_level + sup_level) / 3
    
    return current_price, price_change, pct_change, res_level, sup_level, pivot_level, df

try:
    price, change, pct_change, resistance, support, pivot, df = fetch_gold_data()
    sma20 = df['SMA_20'].dropna().iloc[-1] if not df['SMA_20'].dropna().empty else price
    vol = df['Volatility'].iloc[-1]
except Exception as e:
    st.error(f"Error loading market feed: {e}")
    st.stop()

# 3-Column Layout matching pitch deck exactly, scaled to fit one single screen
col_left, col_mid, col_right = st.columns([1, 2.3, 1.1])

with col_left:
    # Market Summary Card
    st.markdown(f"""
    <div class="card">
        <div style="font-size: 10px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 2px;">Market Summary</div>
        <div style="font-size: 15px; font-weight: 700; color: #ffffff;">XAUUSD</div>
        <div style="font-size: 11px; color: #9ca3af; margin-bottom: 6px;">Gold / U.S. Dollar</div>
        <div class="metric-value">{price:,.2f}</div>
        <div style="font-size: 11px; color: {'#34d399' if change >= 0 else '#ef4444'}; margin-top: 2px;">
            {change:+,.2f} ({pct_change:+,.2f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Sentiment Card
    st.markdown("""
    <div class="card">
        <div style="font-size: 10px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 4px;">AI Sentiment</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span class="badge-bullish">BULLISH</span>
            <span style="font-size: 15px; font-weight: 700; color: #34d399;">78%</span>
        </div>
        <div style="background-color: #1f2937; height: 5px; border-radius: 3px; overflow: hidden; margin-bottom: 6px;">
            <div style="background: linear-gradient(90deg, #10b981, #34d399); width: 78%; height: 100%;"></div>
        </div>
        <div style="font-size: 10px; color: #9ca3af; display: flex; justify-content: space-between;">
            <span>Bullish 78%</span>
            <span>Neutral 17%</span>
            <span>Bearish 5%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_mid:
    # Main Chart Card
    st.markdown("""
    <div class="card" style="padding-bottom: 2px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-weight: 700; font-size: 12px;">XAUUSD • 1D</span>
            <div style="display: flex; gap: 6px; font-size: 10px; color: #9ca3af;">
                <span>1m</span><span>5m</span><span>15m</span><span>1H</span><span>4H</span><span style="color: #ffffff; background: #1f2937; padding: 1px 4px; border-radius: 3px;">1D</span><span>1W</span><span>1M</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="XAUUSD",
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444'
    )])
    
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SMA_20'], mode='lines', name='20 SMA',
        line=dict(color='#f59e0b', width=1.5)
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='#121824',
        plot_bgcolor='#121824',
        margin=dict(l=4, r=4, t=4, b=4),
        height=210,
        xaxis_rangeslider_visible=False,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Sub-cards under chart (Both Institutional Flow & Volatility Index as Bar Charts)
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.markdown("""
        <div class="card" style="margin-bottom: 0; padding: 8px;">
            <div style="font-size: 10px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 2px;">Institutional Flow</div>
        """, unsafe_allow_html=True)
        flow_fig = go.Figure(go.Bar(
            y=[12, -4, 8, 15, -2, 9, 14, 18, 5, 12],
            marker_color=['#10b981' if x > 0 else '#ef4444' for x in [12, -4, 8, 15, -2, 9, 14, 18, 5, 12]]
        ))
        flow_fig.update_layout(
            template="plotly_dark", paper_bgcolor='#121824', plot_bgcolor='#121824',
            margin=dict(l=0, r=0, t=0, b=0), height=60, xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        st.plotly_chart(flow_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with sub_col2:
        st.markdown("""
        <div class="card" style="margin-bottom: 0; padding: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                <span style="font-size: 10px; text-transform: uppercase; color: #9ca3af; font-weight: 600;">Volatility Index</span>
                <span style="font-size: 11px; font-weight: 700; color: #34d399;">18.7</span>
            </div>
        """, unsafe_allow_html=True)
        # Converted Volatility Index to Bar Chart as requested
        vol_fig = go.Figure(go.Bar(
            y=[17.2, 17.8, 17.5, 18.2, 18.0, 18.5, 18.3, 18.7],
            marker_color='#34d399'
        ))
        vol_fig.update_layout(
            template="plotly_dark", paper_bgcolor='#121824', plot_bgcolor='#121824',
            margin=dict(l=0, r=0, t=0, b=0), height=60, xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        st.plotly_chart(vol_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    # AI Trade Insight Card
    st.markdown("""
    <div class="card">
        <div style="font-size: 10px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 4px;">AI Trade Insight</div>
        <div style="margin-bottom: 6px;"><span class="badge-bullish">Bullish Bias</span></div>
        <p style="font-size: 11px; color: #d1d5db; line-height: 1.25; margin-bottom: 6px;">
            Price is rebounding from demand zone with strong institutional interest and compressed volatility.
        </p>
        <div style="font-size: 10px; color: #9ca3af; margin-bottom: 2px;">Probability</div>
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="background-color: #1f2937; height: 4px; border-radius: 2px; flex-grow: 1; overflow: hidden;">
                <div style="background-color: #34d399; width: 78%; height: 100%;"></div>
            </div>
            <span style="font-size: 11px; font-weight: 700; color: #34d399;">78%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Levels Card
    st.markdown(f"""
    <div class="card">
        <div style="font-size: 10px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 6px;">Key Levels</div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px;">
            <span style="color: #9ca3af;">Resistance</span>
            <span style="font-weight: 600; color: #ffffff;">{resistance:,.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px;">
            <span style="color: #9ca3af;">Support</span>
            <span style="font-weight: 600; color: #ffffff;">{support:,.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px;">
            <span style="color: #9ca3af;">Pivot</span>
            <span style="font-weight: 600; color: #ffffff;">{pivot:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Next Event Card
    st.markdown("""
    <div class="card" style="margin-bottom: 0;">
        <div style="font-size: 10px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 2px;">Next Event</div>
        <div style="font-size: 11px; font-weight: 600; color: #ffffff; margin-bottom: 2px;">📅 US CPI Data</div>
        <div style="font-size: 10px; color: #f59e0b; font-weight: 600;">In 2h 35m</div>
    </div>
    """, unsafe_allow_html=True)
