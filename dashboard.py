import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime, timedelta, date
import time
import base64
import requests
import plotly.express as px

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
    "binanceus", "kraken", "coinbasepro","cex", "coinbase", "coinbaseexchange", "coinbaseinternational",
    "coinex", "coinmate", "coinmetro", "coinone", "coinsph", "coinspot", "cryptocom", "cryptomus",
    "defx", "delta", "deribit", "digifinex", "ellipx", "exmo", "fmfwio", "foxbit", "gate", "gemini",
    "hashkey", "hitbtc", "hollaex", "htx", "hyperliquid", "independentreserve", "indodax",
    "krakenfutures", "kucoin", "kucoinfutures"
])

# --- Asset Handling & CSS ---
@st.cache_data
def get_logo_base64(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode()
    except requests.exceptions.RequestException:
        return None

def load_css():
    st.markdown(f'''
    <style>
        :root {{
            --primary-bg: #0A0E1A;
            --card-bg: #1A1F2E;
            --accent-green: #00D084;
            --accent-red: #FF6B6B;
            --accent-blue: #4ECDC4;
            --text-primary: #FFFFFF;
            --text-secondary: #B0B8C1;
            --border-subtle: #2D3748;
        }}
        body {{ background-color: var(--primary-bg); color: var(--text-primary); }}
        .main-title {{ font-size: 2.5rem; font-weight: bold; color: var(--text-primary); margin-bottom: 0.2rem; }}
        .exchange-subtitle {{ font-size: 1.8rem; color: var(--accent-blue); margin-bottom: 1.5rem; }}
        [data-testid="stMetricValue"] {{ color: var(--accent-green); }}
        
        .opportunity-card {{
            background-color: var(--card-bg);
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid var(--border-subtle);
            transition: box-shadow 0.3s ease-in-out;
        }}
        .opportunity-card:hover {{
            box-shadow: 0 8px 25px rgba(78, 205, 196, 0.15);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        .profit-display {{
            font-size: 1.8rem;
            font-weight: bold;
        }}
        .profit-green {{ color: var(--accent-green); }}
        .profit-blue {{ color: var(--accent-blue); }}
        .path-display {{
            font-family: monospace;
            font-size: 1.2rem;
            color: var(--text-secondary);
        }}
        .card-footer {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-subtle);
            padding-top: 1rem;
            margin-top: 1rem;
        }}
        .step-card {{
            background: var(--border-subtle);
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        .trade-info strong {{
            color: var(--text-primary);
        }}
        .market-symbol {{
            font-family: 'monospace';
            font-size: 1.1rem;
            background-color: var(--accent-blue);
            color: var(--text-primary); /* Changed to white for contrast */
            padding: 0.2rem 0.5rem;
            border-radius: 0.3rem;
            font-weight: bold;
        }}
        .price-display {{
            color: var(--text-primary);
            font-size: 1.1rem;
            font-weight: 500;
        }}
        .buy-card-step {{
            border-left: 5px solid var(--accent-green);
        }}
        .sell-card-step {{
            border-left: 5px solid var(--accent-red);
        }}
    </style>
    ''', unsafe_allow_html=True)

# --- Data Caching & Fetching ---
@st.cache_data(ttl=30)
def find_arbitrage_opportunities(exchange_name):
    try:
        # Call the actual detection logic from detector.py
        best_opportunity, best_profit, all_opportunities = asyncio.run(detector.run_detection(exchange_name))
        
        return best_opportunity, best_profit, all_opportunities, datetime.now(), None # No error message if successful
    except Exception as e:
        return None, None, [], datetime.now(), str(e)

# --- UI Components ---

def display_sidebar():
    with st.sidebar:
        st.title("🤖 Arbitrage Intelligence")

        if 'exchange' not in st.session_state:
            st.session_state.exchange = EXCHANGES[0]

        def handle_exchange_change():
            st.cache_data.clear()

        exchange = st.selectbox(
            "Select Exchange", EXCHANGES, key='exchange', on_change=handle_exchange_change
        )

        st.markdown("---")
        st.markdown("### ⚙️ Refresh Settings")
        auto_refresh = st.checkbox("Enable Auto-Refresh", value=True)
        refresh_interval = st.slider("Interval (seconds)", 10, 60, 30, 5)

        if st.button("🔄 Refresh Now", use_container_width=True):
            handle_exchange_change()
            st.rerun()
        
        st.markdown("--- ")
        st.markdown("### 🔎 Filter Opportunities")
        
        # Initialize session state for filters if they don't exist
        if 'search_text' not in st.session_state:
            st.session_state.search_text = ""
        if 'min_profit' not in st.session_state:
            st.session_state.min_profit = 2.5

        st.session_state.search_text = st.text_input("Search by currency...", st.session_state.search_text)
        st.session_state.min_profit = st.slider("Minimum Profit (%)", 0.0, 10.0, st.session_state.min_profit, 0.1)

        st.markdown("---")
        st.markdown("### 📊 Chart Controls")
        # Initialize session state for chart controls
        if 'limit' not in st.session_state:
            st.session_state.limit = 100
        if 'start_date' not in st.session_state:
            st.session_state.start_date = date.today() - timedelta(days=30)
        if 'end_date' not in st.session_state:
            st.session_state.end_date = date.today()

        st.session_state.limit = st.slider("Recent Scans to Display", 50, 500, st.session_state.limit, 10)
        st.session_state.start_date = st.date_input("Start Date", st.session_state.start_date)
        st.session_state.end_date = st.date_input("End Date", st.session_state.end_date)

        st.markdown("---")
        st.caption("Last updated:")
        # last_updated_placeholder is now created in main and updated there.
        # This function no longer returns last_updated_placeholder

    return exchange, auto_refresh, refresh_interval

def display_historical_chart(exchange, limit, start_date, end_date):
    history_df = database.get_historical_profit_trend(exchange, limit, start_date, end_date)
    
    if not history_df.empty:
        with st.expander("📈 View Profitability Trend", expanded=False):
            fig = px.line(
                history_df, x='timestamp', y='profit_percentage',
                title=f'Profitability Over Time for {exchange.upper()}',
                labels={'timestamp': 'Time', 'profit_percentage': 'Profit %'}
            )
            last_point = history_df.iloc[-1]
            fig.add_scatter(
                x=[last_point['timestamp']], y=[last_point['profit_percentage']],
                mode='markers',
                marker=dict(color='var(--accent-green)', size=10, symbol='diamond'),
                name='Latest'
            )
            fig.update_layout(
                template='plotly_dark',
                xaxis_title=None,
                yaxis_title='Profit %',
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No historical data available for the selected criteria.")

def _extract_clean_path(opportunity):
    path = []
    for opp in opportunity:
        if not path:
            path.append(opp.symbol.base)
        if opp.symbol.quote not in path:
            path.append(opp.symbol.quote)
    # Ensure the path loops back to the start
    if path[0] != path[-1]:
        # Find the next logical step to close the loop
        for opp in opportunity:
            if opp.symbol.base == path[-1] and opp.symbol.quote == path[0]:
                break
        else:
            # If no direct loop, just append the start
            path.append(path[0])
    return " → ".join(path)

def display_opportunity_cards(all_opportunities):
    search_text = st.session_state.search_text.upper()
    min_profit = st.session_state.min_profit

    filtered_opportunities = []
    for opp, profit in all_opportunities:
        if (profit - 1) * 100 >= min_profit:
            path = _extract_clean_path(opp)
            if not search_text or search_text in path:
                filtered_opportunities.append((opp, profit, path))

    if not filtered_opportunities:
        st.info("No opportunities match your current filter criteria.")
        return

    st.markdown(f"**Showing {len(filtered_opportunities)} of {len(all_opportunities)} opportunities**")

    for i, (opportunity, profit, path) in enumerate(filtered_opportunities):
        profit_percentage = (profit - 1) * 100
        # The color class logic here assumes all_opportunities is sorted by profit, and the first one is the "best"
        # If all_opportunities only contains the best, then this logic is fine.
        color_class = "profit-green" if i == 0 and profit_percentage == (all_opportunities[0][1] - 1) * 100 else "profit-blue"

        header_html = f"""
        <div class="card-header">
            <div class="profit-display {color_class}">{profit_percentage:.2f}%</div>
            <div class="path-display">{path}</div>
        </div>
        """

        with st.container():
            st.markdown(f'<div class="opportunity-card">{header_html}</div>', unsafe_allow_html=True)
            with st.expander("View Trade Steps"):
                for j, opp in enumerate(opportunity):
                    action = "BUY" if opp.reversed else "SELL"
                    market_symbol = f"{opp.symbol.base}/{opp.symbol.quote}"
                    
                    # Determine step card color based on action
                    step_card_class = "buy-card-step" if action == "BUY" else "sell-card-step"

                    st.markdown(f'''
                    <div class="step-card {step_card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div class="trade-info">
                                <strong>Step {j+1}:</strong> {action} <span class="market-symbol">{market_symbol}</span>
                            </div>
                            <span class="price-display">{opp.last_price:.8f}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

def display_footer():
    logo_base64 = get_logo_base64(LOGO_URL)
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="CryptoPlaza Logo">' if logo_base64 else ""
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

# --- Main App ---

def main():
    load_css()
    
    exchange, auto_refresh, refresh_interval = display_sidebar()

    st.markdown('<div class="main-title">Arbitrage Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="exchange-subtitle">{exchange.upper()}</div>', unsafe_allow_html=True)

    last_updated_placeholder = st.empty() # Moved placeholder creation here

    with st.spinner(f"Scanning {exchange} for opportunities..."):
        best_opportunity, best_profit, all_opportunities, last_updated, error_message = find_arbitrage_opportunities(exchange)

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
        st.error(f"❌ Error connecting to {exchange}: {error_message}")
    elif best_opportunity:
        profit_percentage = (best_profit - 1) * 100
        database.save_arbitrage_run(exchange, profit_percentage, best_opportunity) # Save the best opportunity

        st.metric(label="🎯 Est. Profit Opportunity", value=f"{profit_percentage:.4f}%")
        
        # Pass chart control values from session state
        display_historical_chart(exchange, st.session_state.limit, st.session_state.start_date, st.session_state.end_date)
        
        st.markdown("---")
        display_opportunity_cards(all_opportunities) # Display all (or best) opportunities
    else:
        st.success("✅ No profitable arbitrage opportunities detected at the moment.")
        # Pass chart control values from session state even if no opportunities
        display_historical_chart(exchange, st.session_state.limit, st.session_state.start_date, st.session_state.end_date)

    display_footer()

    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()