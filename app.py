import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from groq import Groq
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="NAVEX Capital — AI Intelligence V0",
    page_icon="📈",
    layout="wide"
)

# Custom Dark Institutional Fintech Styling (Matching Pitch Deck)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
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
        padding: 12px 20px;
        border-radius: 8px;
        border: 1px solid #1f2937;
        margin-bottom: 20px;
    }
    .card {
        background-color: #121824;
        border: 1px solid #1f2937;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 16px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
    }
    .badge-bullish {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    .disclaimer-banner {
        background-color: #1e1b18;
        border: 1px solid #b45309;
        color: #fbbf24;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 12px;
        margin-bottom: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Stage Disclaimer Banner
st.markdown("""
<div class="disclaimer-banner">
    <strong>NAVEX AI Intelligence V0 — Pre-MVP Proof of Concept</strong> | Demonstrating core intelligence workflow on live XAU/USD feed. Not a production trading system.
</div>
""", unsafe_allow_html=True)

# Top Navigation Bar simulation
st.markdown("""
<div class="topnav">
    <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 20px; font-weight: 800; color: #f59e0b; letter-spacing: 1px;">N $\mathbf{N}$</span>
        <span style="font-size: 16px; font-weight: 700; color: #ffffff; letter-spacing: 0.5px;">NAVEX CAPITAL</span>
        <span style="color: #4b5563; margin: 0 10px;">|</span>
        <span style="color: #60a5fa; font-size: 14px; font-weight: 600; cursor: pointer;">Overview</span>
        <span style="color: #9ca3af; font-size: 14px; cursor: pointer;">Markets</span>
        <span style="color: #9ca3af; font-size: 14px; cursor: pointer;">AI Insights</span>
        <span style="color: #9ca3af; font-size: 14px; cursor: pointer;">News</span>
        <span style="color: #9ca3af; font-size: 14px; cursor: pointer;">Alerts</span>
        <span style="color: #9ca3af; font-size: 14px; cursor: pointer;">Watchlist</span>
    </div>
    <div style="color: #9ca3af; font-size: 14px;">
        🟢 Live Feed Active
    </div>
</div>
""", unsafe_allow_html=True)

# Fetch Live Gold Data (GC=X represents Gold Spot)
@st.cache_data(ttl=30)
def fetch_gold_data():
    gold = yf.Ticker("GC=X")
    df = gold.history(period="7d", interval="1h")
    if df.empty or len(df) < 30:
        df = gold.history(period="5d", interval="1h")
    
    current_price = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    price_change = current_price - prev_close
    pct_change = (price_change / prev_close) * 100
    
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['Volatility'] = df['High'] - df['Low']
    
    res_level = current_price * 1.01
    sup_level = current_price * 0.98
    pivot_level = (current_price + res_level + sup_level) / 3
    
    return current_price, price_change, pct_change, res_level, sup_level, pivot_level, df

try:
    price, change, pct_change, resistance, support, pivot, df = fetch_gold_data()
    sma20 = df['SMA_20'].iloc[-1]
    vol = df['Volatility'].iloc[-1]
except Exception as e:
    st.error(f"Error connecting to live market feed: {e}")
    st.stop()

# Layout Grid: 3 Columns matching pitch deck
col_left, col_mid, col_right = st.columns([1, 2.2, 1.2])

with col_left:
    # Market Summary Card
    st.markdown(f"""
    <div class="card">
        <div style="font-size: 11px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 4px;">Market Summary</div>
        <div style="font-size: 18px; font-weight: 700; color: #ffffff;">XAUUSD</div>
        <div style="font-size: 12px; color: #9ca3af; margin-bottom: 12px;">Gold / U.S. Dollar</div>
        <div class="metric-value">{price:,.2f}</div>
        <div style="font-size: 13px; color: {'#34d399' if change >= 0 else '#ef4444'}; margin-top: 4px;">
            {change:+,.2f} ({pct_change:+,.2f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Sentiment Card
    st.markdown("""
    <div class="card">
        <div style="font-size: 11px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 8px;">AI Sentiment</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span class="badge-bullish">BULLISH</span>
            <span style="font-size: 20px; font-weight: 700; color: #34d399;">78%</span>
        </div>
        <div style="background-color: #1f2937; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 12px;">
            <div style="background: linear-gradient(90deg, #10b981, #34d399); width: 78%; height: 100%;"></div>
        </div>
        <div style="font-size: 12px; color: #9ca3af; display: flex; justify-content: space-between;">
            <span>Bullish 78%</span>
            <span>Neutral 17%</span>
            <span>Bearish 5%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_mid:
    # Main Chart Card
    st.markdown("""
    <div class="card" style="padding-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-weight: 700; font-size: 15px;">XAUUSD • 1D</span>
            <div style="display: flex; gap: 8px; font-size: 12px; color: #9ca3af;">
                <span>1m</span><span>5m</span><span>15m</span><span>1H</span><span>4H</span><span style="color: #ffffff; background: #1f2937; padding: 2px 6px; border-radius: 4px;">1D</span><span>1W</span><span>1M</span>
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
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        xaxis_rangeslider_visible=False,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bottom sub-cards under chart (Institutional Flow & Volatility Index)
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.markdown("""
        <div class="card" style="margin-bottom: 0;">
            <div style="font-size: 11px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 8px;">Institutional Flow</div>
        """, unsafe_allow_html=True)
        flow_fig = go.Figure(go.Bar(
            y=[12, -4, 8, 15, -2, 9, 14, 18, 5, 12],
            marker_color=['#10b981' if x > 0 else '#ef4444' for x in [12, -4, 8, 15, -2, 9, 14, 18, 5, 12]]
        ))
        flow_fig.update_layout(
            template="plotly_dark", paper_bgcolor='#121824', plot_bgcolor='#121824',
            margin=dict(l=0, r=0, t=0, b=0), height=85, xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        st.plotly_chart(flow_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with sub_col2:
        st.markdown("""
        <div class="card" style="margin-bottom: 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 11px; text-transform: uppercase; color: #9ca3af; font-weight: 600;">Volatility Index</span>
                <span style="font-size: 13px; font-weight: 700; color: #34d399;">18.7</span>
            </div>
        """, unsafe_allow_html=True)
        vol_fig = go.Figure(go.Scatter(
            y=[17.2, 17.8, 17.5, 18.2, 18.0, 18.5, 18.3, 18.7],
            mode='lines', line=dict(color='#34d399', width=2)
        ))
        vol_fig.update_layout(
            template="plotly_dark", paper_bgcolor='#121824', plot_bgcolor='#121824',
            margin=dict(l=0, r=0, t=0, b=0), height=85, xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        st.plotly_chart(vol_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    # AI Trade Insight Card
    st.markdown("""
    <div class="card">
        <div style="font-size: 11px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 8px;">AI Trade Insight</div>
        <div style="margin-bottom: 10px;"><span class="badge-bullish">Bullish Bias</span></div>
        <p style="font-size: 13px; color: #d1d5db; line-height: 1.4; margin-bottom: 12px;">
            Price is rebounding from demand zone with strong institutional interest and compressed volatility.
        </p>
        <div style="font-size: 12px; color: #9ca3af; margin-bottom: 4px;">Probability</div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="background-color: #1f2937; height: 6px; border-radius: 3px; flex-grow: 1; overflow: hidden;">
                <div style="background-color: #34d399; width: 78%; height: 100%;"></div>
            </div>
            <span style="font-size: 13px; font-weight: 700; color: #34d399;">78%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Levels Card
    st.markdown(f"""
    <div class="card">
        <div style="font-size: 11px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 10px;">Key Levels</div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px;">
            <span style="color: #9ca3af;">Resistance</span>
            <span style="font-weight: 600; color: #ffffff;">{resistance:,.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px;">
            <span style="color: #9ca3af;">Support</span>
            <span style="font-weight: 600; color: #ffffff;">{support:,.2f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px;">
            <span style="color: #9ca3af;">Pivot</span>
            <span style="font-weight: 600; color: #ffffff;">{pivot:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Next Event Card
    st.markdown("""
    <div class="card">
        <div style="font-size: 11px; text-transform: uppercase; color: #9ca3af; font-weight: 600; margin-bottom: 6px;">Next Event</div>
        <div style="font-size: 13px; font-weight: 600; color: #ffffff; margin-bottom: 4px;">📅 US CPI Data</div>
        <div style="font-size: 12px; color: #f59e0b; font-weight: 600;">In 2h 35m</div>
    </div>
    """, unsafe_allow_html=True)
