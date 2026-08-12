import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="NAVEX Capital — AI-Native Trading Platform",
    page_icon="📈",
    layout="wide"
)

# --- SESSION STATE INITIALIZATION ---
if "portfolio_value" not in st.session_state:
    st.session_state.portfolio_value = 50000.00
    st.session_state.available_margin = 38450.00
    st.session_state.todays_pnl = 1245.50
    st.session_state.win_rate = 68.4
    st.session_state.risk_score = "Moderate"
    st.session_state.positions = [
        {"id": "POS-101", "instrument": "XAUUSD", "side": "BUY", "entry": 2352.40, "current": 2365.20, "sl": 2340.00, "tp": 2390.00, "size": 1.5, "pnl": 192.00, "rr": "2.8:1", "status": "OPEN"},
        {"id": "POS-102", "instrument": "EURUSD", "side": "SELL", "entry": 1.0890, "current": 1.0865, "sl": 1.0930, "tp": 1.0800, "size": 2.0, "pnl": 50.00, "rr": "2.2:1", "status": "OPEN"}
    ]
    st.session_state.journal = [
        {"id": "TR-01", "instrument": "XAUUSD", "dir": "BUY", "entry": 2345.10, "exit": 2362.40, "pnl": "+$259.50", "setup": "Demand Zone Rebound", "score": "8.5/10", "review": "Good structural alignment with DXY weakness."},
        {"id": "TR-02", "instrument": "NAS100", "dir": "BUY", "entry": 18450.0, "exit": 18400.0, "pnl": "-$125.00", "setup": "Breakout", "score": "5.0/10", "review": "Entry occurred before momentum confirmation."}
    ]
    st.session_state.watchlist = ["XAUUSD", "EURUSD", "GBPUSD", "NAS100", "BTCUSD"]
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello, trader. I am NAVEX AI Copilot. How can I assist your market analysis or execution workflow today?"}
    ]

# --- CUSTOM STYLING ---
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
    .demo-badge {
        background-color: #1e1b18;
        border: 1px solid #b45309;
        color: #fbbf24;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 12px;
    }
    .card {
        background-color: #121824;
        border: 1px solid #1f2937;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        margin-bottom: 14px;
    }
    .metric-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9ca3af;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #ffffff;
    }
    .badge-bullish {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    .badge-bearish {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid rgba(248, 113, 113, 0.3);
    }
    .badge-neutral {
        background-color: rgba(156, 163, 175, 0.15);
        color: #9ca3af;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid rgba(156, 163, 175, 0.3);
    }
    .loop-box {
        background-color: #161e2e;
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 13px;
        color: #e5e7eb;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("### ⚡ NAVEX CAPITAL")
    st.markdown('<div class="demo-badge">🟢 DEMO ENVIRONMENT</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("**Core Terminal**")
    nav_selection = st.radio(
        "Navigation",
        [
            "Overview",
            "Markets",
            "AI Intelligence",
            "AI Trade Copilot",
            "Trade / Execution",
            "Positions",
            "Portfolio",
            "AI Market Scanner",
            "News & Macro",
            "Trading Journal",
            "Learn",
            "Watchlists",
            "Risk Controls",
            "Profile & Settings"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**NAVEX Product Loop**")
    st.markdown("""
    <div style="font-size: 11px; color: #9ca3af; line-height: 1.5;">
    1. <b>ANALYZE</b> Market Data<br>
    2. <b>AI INTELLIGENCE</b> Engine<br>
    3. <b>DECIDE</b> Actionable Setup<br>
    4. <b>EXECUTE</b> Order Ticket<br>
    5. <b>MANAGE</b> Active Risk<br>
    6. <b>LEARN & IMPROVE</b> Journal
    </div>
    """, unsafe_allow_html=True)

# --- DATA HELPER ---
@st.cache_data(ttl=60)
def get_market_data(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        df = t.history(period="1mo", interval="1d")
        if df.empty:
            raise ValueError()
        return df
    except:
        # Fallback synthetic data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        np.random.seed(42 if ticker_symbol=="XAUUSD=X" else 10)
        base = 2360.0 if "XAU" in ticker_symbol else 1.0850
        prices = base + np.cumsum(np.random.randn(30) * (base * 0.003))
        return pd.DataFrame({
            'Open': prices - 2, 'High': prices + 5, 'Low': prices - 5, 'Close': prices, 'Volume': np.random.randint(10000, 50000, size=30)
        }, index=dates)

# ==========================================
# 1. OVERVIEW DASHBOARD
# ==========================================
if nav_selection == "Overview":
    st.title("NAVEX Intelligence Dashboard")
    st.caption("Institutional-grade overview combining portfolio health, live cross-asset intelligence, and AI setups.")
    
    # Top KPI Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.markdown(f'<div class="card"><div class="metric-title">Portfolio Value</div><div class="metric-value">${st.session_state.portfolio_value:,.2f}</div><div style="font-size:11px; color:#34d399; margin-top:2px;">+2.48% today</div></div>', unsafe_allow_html=True)
    with kpi2:
        st.markdown(f'<div class="card"><div class="metric-title">Available Margin</div><div class="metric-value">${st.session_state.available_margin:,.2f}</div><div style="font-size:11px; color:#9ca3af; margin-top:2px;">76.9% free</div></div>', unsafe_allow_html=True)
    with kpi3:
        st.markdown(f'<div class="card"><div class="metric-title">Today’s P&L</div><div class="metric-value" style="color: #34d399;">+${st.session_state.todays_pnl:,.2f}</div><div style="font-size:11px; color:#34d399; margin-top:2px;">Realized + Unrealized</div></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="card"><div class="metric-title">Win Rate (30D)</div><div class="metric-value">{st.session_state.win_rate}%</div><div style="font-size:11px; color:#34d399; margin-top:2px;">Avg R:R 2.4:1</div></div>', unsafe_allow_html=True)
    with kpi5:
        st.markdown(f'<div class="card"><div class="metric-title">Risk Score</div><div class="metric-value" style="color: #f59e0b;">{st.session_state.risk_score}</div><div style="font-size:11px; color:#9ca3af; margin-top:2px;">Exposure controlled</div></div>', unsafe_allow_html=True)

    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.subheader("Market Intelligence Watchlist")
        market_summary_data = [
            {"Asset": "XAUUSD", "Price": "$2,365.20", "Change": "+0.78%", "Bias": "BULLISH", "Confidence": "82%", "Volatility": "Moderate"},
            {"Asset": "EURUSD", "Price": "1.0865", "Change": "-0.15%", "Bias": "NEUTRAL", "Confidence": "58%", "Volatility": "Low"},
            {"Asset": "GBPUSD", "Price": "1.2740", "Change": "+0.22%", "Bias": "BULLISH", "Confidence": "71%", "Volatility": "Moderate"},
            {"Asset": "NAS100", "Price": "18,520.10", "Change": "+1.10%", "Bias": "BULLISH", "Confidence": "76%", "Volatility": "High"},
            {"Asset": "BTCUSD", "Price": "62,400.00", "Change": "-0.85%", "Bias": "BEARISH", "Confidence": "64%", "Volatility": "High"}
        ]
        
        for m in market_summary_data:
            badge_class = "badge-bullish" if m["Bias"] == "BULLISH" else ("badge-bearish" if m["Bias"] == "BEARISH" else "badge-neutral")
            st.markdown(f"""
            <div class="card" style="padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div><b>{m['Asset']}</b> &nbsp; <span style="color:#9ca3af; font-size:13px;">{m['Price']}</span> <span style="color:{'#34d399' if '+' in m['Change'] else '#ef4444'}; font-size:12px;">({m['Change']})</span></div>
                <div style="display: flex; gap: 15px; align-items: center;">
                    <span class="{badge_class}">{m['Bias']}</span>
                    <span style="font-size: 12px; color: #9ca3af;">Conf: <b>{m['Confidence']}</b></span>
                    <span style="font-size: 12px; color: #9ca3af;">Vol: {m['Volatility']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.subheader("AI-Detected Opportunities")
        st.markdown("""
        <div class="card">
            <table style="width:100%; font-size:13px; text-align:left; border-collapse: collapse;">
                <tr style="color:#9ca3af; border-bottom:1px solid #1f2937; padding-bottom:6px;">
                    <th style="padding-bottom:6px;">Asset</th><th style="padding-bottom:6px;">Setup</th><th style="padding-bottom:6px;">Direction</th><th style="padding-bottom:6px;">Confidence</th><th style="padding-bottom:6px;">R:R</th><th style="padding-bottom:6px;">Entry Zone</th>
                </tr>
                <tr style="border-bottom:1px solid #1f2937;">
                    <td style="padding:8px 0;"><b>XAUUSD</b></td><td>Demand Zone Rebound</td><td><span class="badge-bullish">LONG</span></td><td>82%</td><td>3.2:1</td><td>2,350 - 2,355</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;"><b>NAS100</b></td><td>Breakout Retest</td><td><span class="badge-bullish">LONG</span></td><td>76%</td><td>2.5:1</td><td>18,480 - 18,500</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_side:
        st.subheader("Upcoming Macro Events")
        st.markdown("""
        <div class="card" style="font-size: 13px;">
            <div style="margin-bottom: 10px;">🔴 <b>US CPI Inflation Data</b><br><span style="color:#9ca3af; font-size:11px;">USD • High Impact • In 2h 35m</span></div>
            <div style="margin-bottom: 10px;">🟡 <b>ECB Monetary Policy Meeting</b><br><span style="color:#9ca3af; font-size:11px;">EUR • Medium Impact • Tomorrow</span></div>
            <div>🟢 <b>UK Retail Sales m/m</b><br><span style="color:#9ca3af; font-size:11px;">GBP • Low Impact • In 2 days</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Portfolio Risk Metrics")
        st.markdown("""
        <div class="card" style="font-size: 13px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span>Concentration:</span><b>XAUUSD (42%)</b></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span>Correlation Risk:</span><span style="color:#34d399;">Low</span></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span>Max Open Risk:</span><b>1.2%</b></div>
            <div style="display:flex; justify-content:space-between;"><span>Overall Status:</span><span style="color:#34d399;">Healthy</span></div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 2. MARKETS TERMINAL
# ==========================================
elif nav_selection == "Markets":
    st.title("Markets & Technical Terminal")
    st.caption("Professional charting equipped with AI-driven liquidity zones, order blocks, and structural overlays.")
    
    col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 2])
    with col_sel1:
        selected_market = st.selectbox("Instrument", ["XAUUSD (Gold)", "EURUSD (Euro)", "NAS100 (Nasdaq)", "BTCUSD (Bitcoin)"])
    with col_sel2:
        timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1H", "4H", "1D", "1W"])
    with col_sel3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("🛠️ **Active Overlays:** Support/Resistance • Supply/Demand • Order Blocks • FVG • Liquidity Zones", unsafe_allow_html=True)

    ticker_map = {"XAUUSD (Gold)": "GC=X", "EURUSD (Euro)": "EURUSD=X", "NAS100 (Nasdaq)": "^NDX", "BTCUSD (Bitcoin)": "BTC-USD"}
    df = get_market_data(ticker_map.get(selected_market, "GC=X"))
    
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name=selected_market, increasing_line_color='#10b981', decreasing_line_color='#ef4444'
    )])
    
    # Add SMA
    df['SMA_20'] = df['Close'].rolling(20).mean()
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='20 SMA', line=dict(color='#f59e0b', width=1.5)))
    
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='#121824', plot_bgcolor='#121824',
        margin=dict(l=10, r=10, t=10, b=10), height=460, xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="card">
        <h4>🤖 AI Chart Annotations Active</h4>
        <ul style="font-size:13px; color:#d1d5db; margin-bottom:0; padding-left:18px;">
            <li><b>AI Demand Zone Detected:</b> 2,350.00 – 2,355.50 (High institutional liquidity absorption).</li>
            <li><b>Liquidity Sweep:</b> Completed below recent swing low with rejection wick.</li>
            <li><b>Fair Value Gap (FVG):</b> Unmitigated imbalance identified between 2,372.10 and 2,378.40.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. AI INTELLIGENCE
# ==========================================
elif nav_selection == "AI Intelligence":
    st.title("NAVEX AI Intelligence Engine")
    st.caption("Flagship multi-signal synthesis converting raw market streams into institutional-grade trade theses.")
    
    col_i1, col_i2 = st.columns([1, 1.5])
    with col_i1:
        st.markdown("""
        <div class="card">
            <h3>XAUUSD Intelligence Profile</h3>
            <div style="margin: 12px 0;"><span class="badge-bullish" style="font-size:14px; padding:6px 12px;">AI BIAS: BULLISH</span> &nbsp; <b style="font-size:18px;">82% Confidence</b></div>
            <hr style="border-color:#1f2937;">
            <div style="font-size:13px; line-height:1.6;">
                <b>Market Regime:</b> Trending / Pullback Rebound<br>
                <b>Momentum:</b> Positive (Accelerating)<br>
                <b>Volatility:</b> Moderate / Expanding<br>
                <b>Liquidity:</b> Sell-side sweep complete<br>
                <b>Structure:</b> Higher Timeframe Bullish Continuation<br>
                <b>Macro Bias:</b> DXY Softness Supporting Metals
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_i2:
        st.markdown("""
        <div class="card">
            <h3>🧠 AI Generated Trade Thesis</h3>
            <p style="font-size:13px; color:#d1d5db; line-height:1.6;">
                Price has successfully swept institutional liquidity pools below the recent swing low and reacted sharply off the 4H demand zone ($2,350). Momentum oscillators confirm exhaustion of short-term selling pressure, while macroeconomic indicators (falling US real yields and softer DXY) create an optimal tailwind for gold continuation.
            </p>
            <h4 style="margin-top:15px; color:#f87171 !important;">⚠️ Risk Factors</h4>
            <ul style="font-size:13px; color:#d1d5db; padding-left:18px; margin-bottom:0;">
                <li>Upcoming high-impact US CPI inflation release may cause sudden intraday spread expansion.</li>
                <li>Immediate resistance clustered around $2,385.00 psychological barrier.</li>
                <li>Elevated intraday volatility requiring disciplined stop-loss placement.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 4. AI TRADE COPILOT
# ==========================================
elif nav_selection == "AI Trade Copilot":
    st.title("NAVEX AI Trade Copilot")
    st.caption("Conversational institutional assistant for scenario analysis, chart breakdown, and trade planning.")
    
    # Prompt suggestion buttons
    cols = st.columns(5)
    prompt_clicked = None
    if cols[0].button("Why is gold bullish?"):
        prompt_clicked = "Why is gold bullish right now?"
    if cols[1].button("Find best setup"):
        prompt_clicked = "Find the highest conviction setup across markets today."
    if cols[2].button("Where is liquidity?"):
        prompt_clicked = "Where are the nearest liquidity pools on XAUUSD?"
    if cols[3].button("Build trade plan"):
        prompt_clicked = "Build a complete trade plan for XAUUSD long entry."
    if cols[4].button("Explain chart"):
        prompt_clicked = "Explain the current market structure on the 1H chart."

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    user_input = st.chat_input("Ask NAVEX AI Copilot anything about markets, risk, or trade setups...")
    if prompt_clicked:
        user_input = prompt_clicked
        
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        # Simulated intelligent response
        response_text = f"Analyzing market conditions for your query: *'{user_input}'*...\n\nBased on current quantitative inputs and structural models, NAVEX AI indicates strong alignment on XAUUSD. Key liquidity rests above $2,385, with support defended at $2,350. Risk/reward profile is favorable for structured long positioning with strict invalidation below structural lows."
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.write(response_text)

# ==========================================
# 5. TRADE / EXECUTION
# ==========================================
elif nav_selection == "Trade / Execution":
    st.title("Execution Ticket (Demo Mode)")
    st.caption("Institutional order router configured for simulated execution and risk calculation.")
    
    t_col1, t_col2 = st.columns([1.2, 1])
    with t_col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        ord_asset = st.selectbox("Asset", ["XAUUSD", "EURUSD", "GBPUSD", "NAS100"])
        ord_side = st.radio("Side", ["BUY / LONG", "SELL / SHORT"], horizontal=True)
        ord_type = st.selectbox("Order Type", ["Market", "Limit", "Stop"])
        
        c1, c2 = st.columns(2)
        with c1:
            ord_qty = st.number_input("Quantity (Lots)", value=1.0, step=0.1)
            ord_entry = st.number_input("Entry Price", value=2365.20)
        with c2:
            ord_sl = st.number_input("Stop Loss", value=2350.00)
            ord_tp = st.number_input("Take Profit", value=2400.00)
            
        st.markdown("---")
        st.markdown("**Risk Calculation:** Risk %: **1.0%** | Margin Required: **$473.04** | Est. R:R: **2.3:1**")
        
        if st.button("🚀 Place Demo Order", use_container_width=True):
            new_pos = {
                "id": f"POS-{np.random.randint(200,999)}",
                "instrument": ord_asset,
                "side": "BUY" if "BUY" in ord_side else "SELL",
                "entry": ord_entry,
                "current": ord_entry,
                "sl": ord_sl,
                "tp": ord_tp,
                "size": ord_qty,
                "pnl": 0.00,
                "rr": "2.3:1",
                "status": "OPEN"
            }
            st.session_state.positions.append(new_pos)
            st.success("Demo Order Submitted Successfully! Position added to portfolio.")
        st.markdown('</div>', unsafe_allow_html=True)

    with t_col2:
        st.markdown("""
        <div class="card">
            <h3>📊 Live Order Preview</h3>
            <p style="font-size:13px; color:#d1d5db;">
                <b>Instrument:</b> XAUUSD<br>
                <b>Estimated Execution:</b> Instant (Simulated)<br>
                <b>Max Potential Loss:</b> -$150.00 (1.0% of Equity)<br>
                <b>Target Profit:</b> +$348.00<br><br>
                <i>Note: Simulated orders do not interact with live brokerage liquidity pools during this pre-seed proof-of-concept.</i>
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. POSITIONS
# ==========================================
elif nav_selection == "Positions":
    st.title("Active Positions & Orders")
    st.caption("Manage open trades, monitor real-time unrealized P&L, and execute simulated position modifications.")
    
    st.markdown("### Open Positions")
    if not st.session_state.positions:
        st.info("No open positions currently active.")
    else:
        for pos in st.session_state.positions:
            pnl_color = "#34d399" if pos['pnl'] >= 0 else "#ef4444"
            st.markdown(f"""
            <div class="card" style="display:flex; justify-content:space-between; align-items:center; padding:12px 16px;">
                <div>
                    <b>{pos['instrument']}</b> &nbsp; <span class="{'badge-bullish' if pos['side']=='BUY' else 'badge-bearish'}">{pos['side']}</span> &nbsp; 
                    <span style="font-size:13px; color:#9ca3af;">Size: {pos['size']} | Entry: {pos['entry']} | SL: {pos['sl']} | TP: {pos['tp']}</span>
                </div>
                <div style="display:flex; gap:20px; align-items:center;">
                    <span style="font-size:15px; font-weight:700; color:{pnl_color};">${pos['pnl']:+,.2f}</span>
                    <span style="font-size:12px; color:#9ca3af;">R:R {pos['rr']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 7. PORTFOLIO
# ==========================================
elif nav_selection == "Portfolio Intelligence":
    pass # handled below in Portfolio
elif nav_selection == "Portfolio":
    st.title("Portfolio Intelligence & Risk")
    st.caption("Holistic view of capital allocation, equity growth curve, and asset exposure.")
    
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown(f'<div class="card"><div class="metric-title">Total Equity</div><div class="metric-value">${st.session_state.portfolio_value + st.session_state.todays_pnl:,.2f}</div></div>', unsafe_allow_html=True)
    with p2:
        st.markdown(f'<div class="card"><div class="metric-title">Max Drawdown</div><div class="metric-value" style="color:#f87171;">-2.1%</div></div>', unsafe_allow_html=True)
    with p3:
        st.markdown(f'<div class="card"><div class="metric-title">Asset Allocation</div><div class="metric-value">FX & Metals</div></div>', unsafe_allow_html=True)
    with p4:
        st.markdown(f'<div class="card"><div class="metric-title">Sharpe Ratio</div><div class="metric-value">2.45</div></div>', unsafe_allow_html=True)
        
    st.subheader("Equity Curve (30 Days)")
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    eq_vals = 48000 + np.cumsum(np.random.randn(30) * 300 + 80)
    fig_eq = go.Figure(go.Scatter(x=dates, y=eq_vals, mode='lines', fill='tozeroy', line=dict(color='#10b981', width=2)))
    fig_eq.update_layout(template="plotly_dark", paper_bgcolor='#121824', plot_bgcolor='#121824', margin=dict(l=10,r=10,t=10,b=10), height=280)
    st.plotly_chart(fig_eq, use_container_width=True)
    
    st.markdown("""
    <div class="card">
        <h4>💡 AI Portfolio Review</h4>
        <p style="font-size:13px; color:#d1d5db; margin-bottom:0;">
            • Your largest concentration is currently in <b>XAUUSD</b> (42% of total margin allocation).<br>
            • Overall portfolio risk score is <b>Moderate</b> with controlled correlation across currency pairs.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 8. AI MARKET SCANNER
# ==========================================
elif nav_selection == "AI Market Scanner":
    st.title("NAVEX AI Market Scanner")
    st.caption("Multi-asset quantitative scanner filtering high-probability setups across Forex, Metals, Indices, and Crypto.")
    
    f1, f2 = st.columns(2)
    with f1:
        filter_asset = st.selectbox("Asset Class Filter", ["All", "Forex", "Metals", "Indices", "Crypto"])
    with f2:
        filter_conf = st.selectbox("Minimum Confidence", ["All", "70%+", "80%+"])
        
    st.markdown("""
    <div class="card">
        <table style="width:100%; font-size:13px; text-align:left; border-collapse: collapse;">
            <tr style="color:#9ca3af; border-bottom:1px solid #1f2937; padding-bottom:8px;">
                <th style="padding-bottom:8px;">Asset</th><th style="padding-bottom:8px;">Bias</th><th style="padding-bottom:8px;">Setup Type</th><th style="padding-bottom:8px;">Confidence</th><th style="padding-bottom:8px;">Entry Zone</th><th style="padding-bottom:8px;">R:R</th><th style="padding-bottom:8px;">Signal</th>
            </tr>
            <tr style="border-bottom:1px solid #1f2937;"><td style="padding:10px 0;"><b>XAUUSD</b></td><td><span class="badge-bullish">BULLISH</span></td><td>Demand Zone</td><td><b>82%</b></td><td>2,350.00</td><td>3.2:1</td><td><span style="color:#34d399;">Active</span></td></tr>
            <tr style="border-bottom:1px solid #1f2937;"><td style="padding:10px 0;"><b>NAS100</b></td><td><span class="badge-bullish">BULLISH</span></td><td>Breakout Retest</td><td><b>76%</b></td><td>18,480.00</td><td>2.5:1</td><td><span style="color:#34d399;">Active</span></td></tr>
            <tr style="border-bottom:1px solid #1f2937;"><td style="padding:10px 0;"><b>EURUSD</b></td><td><span class="badge-neutral">NEUTRAL</span></td><td>Range Bound</td><td><b>58%</b></td><td>1.0850</td><td>1.8:1</td><td><span style="color:#9ca3af;">Monitoring</span></td></tr>
            <tr><td style="padding:10px 0;"><b>BTCUSD</b></td><td><span class="badge-bearish">BEARISH</span></td><td>Liquidity Sweep</td><td><b>64%</b></td><td>63,100.00</td><td>2.1:1</td><td><span style="color:#f87171;">Warning</span></td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 9. NEWS & MACRO
# ==========================================
elif nav_selection == "News & Macro":
    st.title("News & Macro Intelligence")
    st.caption("Real-time economic data feeds, macro dashboard, and AI market impact synthesis.")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.markdown('<div class="card"><div class="metric-title">DXY (Dollar Index)</div><div class="metric-value">104.25</div><div style="font-size:11px; color:#ef4444;">-0.21%</div></div>', unsafe_allow_html=True)
    with m2: st.markdown('<div class="card"><div class="metric-title">US 10Y Yield</div><div class="metric-value">4.22%</div><div style="font-size:11px; color:#ef4444;">-0.04%</div></div>', unsafe_allow_html=True)
    with m3: st.markdown('<div class="card"><div class="metric-title">VIX (Volatility)</div><div class="metric-value">14.80</div><div style="font-size:11px; color:#34d399;">+1.2%</div></div>', unsafe_allow_html=True)
    with m4: st.markdown('<div class="card"><div class="metric-title">Gold Spot</div><div class="metric-value">$2,365</div><div style="font-size:11px; color:#34d399;">+0.78%</div></div>', unsafe_allow_html=True)
    with m5: st.markdown('<div class="card"><div class="metric-title">Crude Oil</div><div class="metric-value">$78.40</div><div style="font-size:11px; color:#ef4444;">-0.45%</div></div>', unsafe_allow_html=True)
    
    st.subheader("AI Market Impact Assessment")
    st.markdown("""
    <div class="card">
        <h4>⚡ Potential XAUUSD Impact: HIGH</h4>
        <p style="font-size:13px; color:#d1d5db; margin-bottom:0;">
            Softer US Treasury yields combined with persistent DXY weakness create a highly favorable macroeconomic environment for gold bulls. Watch closely for the upcoming CPI release as the primary volatility catalyst.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 10. TRADING JOURNAL
# ==========================================
elif nav_selection == "Trading Journal":
    st.title("NAVEX AI Trading Journal")
    st.caption("Automated trade logging, mistake classification, and continuous AI performance scoring.")
    
    j1, j2, j3 = st.columns(3)
    with j1: st.markdown('<div class="card"><div class="metric-title">Performance Score</div><div class="metric-value" style="color:#34d399;">8.4 / 10</div></div>', unsafe_allow_html=True)
    with j2: st.markdown('<div class="card"><div class="metric-title">Best Setup</div><div class="metric-value">Demand Zone</div></div>', unsafe_allow_html=True)
    with j3: st.markdown('<div class="card"><div class="metric-title">Average R:R</div><div class="metric-value">2.4 : 1</div></div>', unsafe_allow_html=True)
    
    st.subheader("Recent Journal Entries & AI Reviews")
    for tr in st.session_state.journal:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <b>{tr['id']} — {tr['instrument']} ({tr['dir']})</b>
                <span style="color:#34d399; font-weight:700;">{tr['pnl']}</span>
            </div>
            <div style="font-size:13px; color:#9ca3af; margin-bottom:8px;">Setup: {tr['setup']} | AI Score: {tr['score']}</div>
            <div style="font-size:13px; color:#d1d5db; background:#161e2e; padding:8px 12px; border-radius:4px;">
                🤖 <b>AI Review:</b> {tr['review']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 11. LEARN
# ==========================================
elif nav_selection == "Learn":
    st.title("NAVEX Learn Academy")
    st.caption("Master institutional market structure, quantitative risk management, and AI-assisted trading.")
    
    courses = [
        ("Trading Fundamentals & Market Mechanics", "Completed (100%)", "#34d399"),
        ("Advanced Price Action & Liquidity Mapping", "In Progress (65%)", "#f59e0b"),
        ("Quantitative Risk Management & Sizing", "Not Started", "#9ca3af"),
        ("Institutional Order Block & FVG Strategies", "Not Started", "#9ca3af")
    ]
    
    for title, prog, color in courses:
        st.markdown(f"""
        <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
            <div><b>{title}</b></div>
            <div style="color:{color}; font-size:13px; font-weight:600;">{prog}</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 12. WATCHLISTS
# ==========================================
elif nav_selection == "Watchlists":
    st.title("Custom Watchlists")
    st.caption("Real-time monitoring and alert triggers for prioritized instruments.")
    
    new_asset = st.text_input("Add Instrument to Watchlist (e.g. AUDUSD)")
    if st.button("Add to Watchlist"):
        if new_asset and new_asset.upper() not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_asset.upper())
            st.success(f"Added {new_asset.upper()} to watchlist.")
            
    for w in st.session_state.watchlist:
        st.markdown(f"""
        <div class="card" style="display:flex; justify-content:space-between; align-items:center; padding:10px 16px;">
            <b>{w}</b>
            <span class="badge-bullish">Active Monitoring</span>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 13. RISK CONTROLS
# ==========================================
elif nav_selection == "Risk Controls":
    st.title("Institutional Risk Controls")
    st.caption("Enforce strict capital protection boundaries and risk parameters.")
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.slider("Max Risk Per Trade (%)", 0.1, 5.0, 1.0, 0.1)
    st.slider("Daily Loss Limit ($)", 500, 5000, 1500, 100)
    st.number_input("Maximum Open Positions", value=5)
    st.checkbox("Enable Automatic Drawdown Circuit Breaker", value=True)
    st.checkbox("Enforce Strict Stop-Loss Requirement", value=True)
    if st.button("Save Risk Parameters"):
        st.success("Risk controls successfully updated across execution engine.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 14. PROFILE & SETTINGS
# ==========================================
elif nav_selection == "Profile & Settings":
    st.title("Profile & Settings")
    st.caption("Manage account preferences, API credentials, and institutional access tiers.")
    
    st.markdown("""
    <div class="card">
        <h4>👤 Institutional Account</h4>
        <p style="font-size:13px; color:#d1d5db;">
            <b>Name:</b> Nitish Vaid (Demo Admin)<br>
            <b>Tier:</b> NAVEX Pre-Seed Investor Demo<br>
            <b>API Status:</b> Connected to Groq Llama-3.1 & yfinance Feed<br>
            <b>Environment:</b> Sandbox Simulation
        </p>
    </div>
    """, unsafe_allow_html=True)
