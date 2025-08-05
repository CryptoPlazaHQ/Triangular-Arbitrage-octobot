import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime, timedelta
import time
import base64
import requests

from triangular_arbitrage import detector, database

# --- Page Configuration & Initialization ---
st.set_page_config(
    page_title="Arbitrage Board by CryptoPlaza",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
database.init_db()

# --- Static Assets & Constants ---
LOGO_URL = "https://raw.githubusercontent.com/CryptoPlazaHQ/Stock/main/cryptoplaza_logo_white.png"
EXCHANGES = sorted([
    "binance", "binanceus", "kraken", "coinbasepro", "binancecoinm", "binanceusdm",
    "bybit", "cex", "coinbase", "coinbaseexchange", "coinbaseinternational", "coincatch", "coincheck",
    "coinex", "coinmate", "coinmetro", "coinone", "coinsph", "coinspot", "cryptocom", "cryptomus",
    "defx", "delta", "deribit", "digifinex", "ellipx", "exmo", "fmfwio", "foxbit", "gate", "gemini",
    "hashkey", "hitbtc", "hollaex", "htx", "hyperliquid", "independentreserve", "indodax",
    "krakenfutures", "kucoin", "kucoinfutures"
])

# --- Asset Handling ---
@st.cache_data
def get_logo_base64(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode()
    except requests.exceptions.RequestException:
        return None

logo_base64 = get_logo_base64(LOGO_URL)
logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="CryptoPlaza Logo">' if logo_base64 else ""

# --- Custom CSS ---
st.markdown(f"""
<style>
    body {{ background-color: #0E1117; color: #FAFAFA; }}
    .main-title {{ font-size: 2.5rem; font-weight: bold; color: #F5F5F5; margin-bottom: 0.2rem; }}
    .exchange-subtitle {{ font-size: 1.8rem; color: #00A79D; margin-bottom: 1.5rem; }}
    [data-testid="stMetricValue"] {{ color: #00FF41; }}
    .metric-card {{
        padding: 1.5rem; border-radius: 0.75rem; background: #1E222A;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4); margin-bottom: 1rem; color: white;
        border-left: 5px solid #444; transition: transform 0.2s;
    }}
    .metric-card:hover {{ transform: scale(1.02); }}
    .buy-card {{ border-left-color: #00FF41; }}
    .sell-card {{ border-left-color: #FF4B4B; }}
    .step-number {{ font-weight: bold; font-size: 1.5rem; color: #888; margin-bottom: 0.5rem; }}
    .trade-info {{ font-size: 1.1rem; }}
    .trade-info strong {{ color: #00A79D; }}
    .market-symbol {{
        font-family: 'monospace'; font-size: 1.2rem; background-color: #2b303b;
        padding: 0.2rem 0.5rem; border-radius: 0.3rem;
    }}
    .latency-fresh {{ color: #00FF41; }}
    .latency-stale {{ color: #FFA500; }}
    .latency-old {{ color: #FF4B4B; }}
    .footer {{
        text-align: center; padding: 2rem 0; color: #888;
    }}
    .footer img {{ width: 150px; margin-bottom: 1rem; }}
</style>
""", unsafe_allow_html=True)

# --- Data Caching & Fetching ---
@st.cache_data(ttl=30)
def find_arbitrage_opportunities(exchange_name):
    try:
        opportunities, profit = asyncio.run(detector.run_detection(exchange_name))
        return opportunities, profit, datetime.now()
    except Exception as e:
        # This error will be displayed in the main body of the app.
        return None, None, datetime.now(), str(e)

# --- Sidebar & State Management ---

def handle_exchange_change():
    """Callback to clear cache when the exchange is changed."""
    st.cache_data.clear()

with st.sidebar:
    st.title("🤖 Triangular Arbitrage")
    
    # Use session state to keep track of the selected exchange
    if 'exchange' not in st.session_state:
        st.session_state.exchange = EXCHANGES[0]

    exchange = st.selectbox(
        "Select Exchange", 
        EXCHANGES, 
        key='exchange', 
        on_change=handle_exchange_change
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Refresh Settings")
    auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
    refresh_interval = st.slider("Interval (seconds)", 10, 60, 30, 5)
    
    if st.button("🔄 Refresh Now", use_container_width=True):
        handle_exchange_change() # Clear cache on manual refresh too
        st.rerun()

    st.markdown("---")
    st.caption("Last updated:")
    last_updated_placeholder = st.empty()

# --- Main Body ---
st.markdown('<div class="main-title">Arbitrage Dashboard</div>', unsafe_allow_html=True)
st.markdown(f'<div class="exchange-subtitle">{st.session_state.exchange.upper()}</div>', unsafe_allow_html=True)

with st.spinner(f"Scanning {st.session_state.exchange} for opportunities..."):
    fetch_result = find_arbitrage_opportunities(st.session_state.exchange)

# Unpack results, including a potential error message
if len(fetch_result) == 4:
    opportunities, profit, last_updated, error_message = fetch_result
else:
    opportunities, profit, last_updated = fetch_result
    error_message = None

def get_latency_color(ts):
    age = datetime.now() - ts
    if age < timedelta(seconds=15): return "fresh"
    if age < timedelta(seconds=30): return "stale"
    return "old"

last_updated_placeholder.markdown(
    f'<span class="latency-{get_latency_color(last_updated)}">{last_updated.strftime("%Y-%m-%d %H:%M:%S")}</span>',
    unsafe_allow_html=True
)

if error_message:
    st.error(f"❌ Error connecting to {st.session_state.exchange}: {error_message}")
elif opportunities:
    profit_percentage = (profit - 1) * 100
    database.save_arbitrage_run(st.session_state.exchange, profit_percentage, opportunities)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="🎯 Est. Profit Opportunity", value=f"{profit_percentage:.4f}%")
    with col2:
        st.markdown("##### Profit Trend (Last 100 Scans)")
        history_df = database.get_historical_profit_trend(st.session_state.exchange, limit=100)
        if not history_df.empty:
            st.line_chart(history_df.set_index('timestamp')['profit_percentage'], use_container_width=True)

    st.markdown("---")
    st.markdown("## 📦 Trade Sequence")

    trade_data_for_export = []
    for i, opp in enumerate(opportunities):
        action = "BUY" if opp.reversed else "SELL"
        market_symbol = f"{opp.symbol.base}/{opp.symbol.quote}"
        st.markdown(f'''
        <div class="metric-card {"buy-card" if action == "BUY" else "sell-card"}">
            <div class="step-number">Step {i+1}</div>
            <div class="trade-info">
                <strong>Action:</strong> {action} <span class="market-symbol">{market_symbol}</span><br>
                <strong>Price:</strong> {opp.last_price:.8f} {opp.symbol.quote}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        trade_data_for_export.append({
            "Step": i + 1, "Market": market_symbol, "Action": action,
            "Base": opp.symbol.base, "Quote": opp.symbol.quote, "Price": opp.last_price
        })

    st.markdown("---")
    st.download_button(
        label="💾 Download Sequence as CSV",
        data=pd.DataFrame(trade_data_for_export).to_csv(index=False).encode("utf-8"),
        file_name=f"arbitrage_{st.session_state.exchange}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.success("✅ No profitable arbitrage opportunities detected at the moment.")

# --- Footer & Disclaimer ---
st.markdown("---")
st.markdown(f'''
    <div class="footer">
        <p>Made by</p>
        {logo_html}
    </div>
''', unsafe_allow_html=True)
st.caption(
    "**Disclaimer:** This tool is for educational and research purposes only. It is not financial advice. "
    "Cryptocurrency trading involves substantial risk, and you should only trade with funds you can afford to lose. "
    "The developers and CryptoPlaza are not responsible for any financial losses incurred. "
    "Always perform your own due diligence."
)

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
