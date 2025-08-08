check fixes.md so you can be waware of last working code and the logic, the current project where          │
│   you have acces have some improvements, displaying more opportunities and so on, however something is       │
│   breaking the code in the errors.md you can find what the last agent was trying to achieve, the think       │
│   is the logic remain intact by enhanving UI/UX dark mode and functionality cleraing displaying cards        │
│   info step ell structure, can you ac as software enginner data visualization senior designer and make       │
│   a great job?      here you have a reference of main code to understand where we come from and respect arbitrage detector logic and database manaGEMENT         



detector.py

# pylint: disable=W0702, C0325

import ccxt.async_support as ccxt
from typing import List, Tuple
from dataclasses import dataclass
import networkx as nx

import octobot_commons.symbols as symbols
import octobot_commons.constants as constants


@dataclass
class ShortTicker:
    symbol: symbols.Symbol
    last_price: float
    reversed: bool = False


async def fetch_tickers(exchange):
    return await exchange.fetch_tickers() if exchange.has['fetchTickers'] else []


def get_symbol_from_key(key_symbol: str) -> symbols.Symbol:
    try:
        return symbols.parse_symbol(key_symbol)
    except:
        return None


def is_delisted_symbols(exchange_time, ticker,
                        threshold=1 * constants.DAYS_TO_SECONDS * constants.MSECONDS_TO_SECONDS) -> bool:
    ticker_time = ticker['timestamp']
    return ticker_time is not None and not (exchange_time - ticker_time <= threshold)


def get_last_prices(exchange_time, tickers, ignored_symbols, whitelisted_symbols=None):
    return [
        ShortTicker(symbol=get_symbol_from_key(key),
                    last_price=tickers[key]['close'])
        for key, _ in tickers.items()
        if tickers[key]['close'] is not None
           and not is_delisted_symbols(exchange_time, tickers[key])
           and str(get_symbol_from_key(key)) not in ignored_symbols
           and (whitelisted_symbols is None or str(get_symbol_from_key(key)) in whitelisted_symbols)
    ]


def get_best_triangular_opportunity(tickers: List[ShortTicker]) -> Tuple[List[ShortTicker], float]:
    # Build a directed graph of currencies
    return get_best_opportunity(tickers, 3)


def get_best_opportunity(tickers: List[ShortTicker], max_cycle: int = 10) -> Tuple[List[ShortTicker], float]:
    # Build a directed graph of currencies
    graph = nx.DiGraph()

    for ticker in tickers:
        if ticker.symbol is not None:
            graph.add_edge(ticker.symbol.base, ticker.symbol.quote, ticker=ticker)
            graph.add_edge(ticker.symbol.quote, ticker.symbol.base,
                           ticker=ShortTicker(symbols.Symbol(f"{ticker.symbol.quote}/{ticker.symbol.base}"),
                                              1 / ticker.last_price, reversed=True))

    best_profit = 1
    best_cycle = None

    # Find all cycles in the graph with a length <= max_cycle
    for cycle in nx.simple_cycles(graph):
        if len(cycle) > max_cycle:
            continue  # Skip cycles longer than max_cycle

        profit = 1
        tickers_in_cycle = []

        # Calculate the profits along the cycle
        for i, base in enumerate(cycle):
            quote = cycle[(i + 1) % len(cycle)]  # Wrap around to complete the cycle
            ticker = graph[base][quote]['ticker']
            tickers_in_cycle.append(ticker)
            profit *= ticker.last_price

        if profit > best_profit:
            best_profit = profit
            best_cycle = tickers_in_cycle

    if best_cycle is not None:
        best_cycle = [
            ShortTicker(symbols.Symbol(f"{ticker.symbol.quote}/{ticker.symbol.base}"), 1 / ticker.last_price, reversed=True)
            if ticker.reversed else ticker
            for ticker in best_cycle
        ]

    return best_cycle, best_profit


async def get_exchange_data(exchange_name):
    exchange_class = getattr(ccxt, exchange_name)
    exchange = exchange_class()
    tickers = await fetch_tickers(exchange)
    exchange_time = exchange.milliseconds()
    await exchange.close()
    return tickers, exchange_time


async def get_exchange_last_prices(exchange_name, ignored_symbols, whitelisted_symbols=None):
    tickers, exchange_time = await get_exchange_data(exchange_name)
    last_prices = get_last_prices(exchange_time, tickers, ignored_symbols, whitelisted_symbols)
    return last_prices


async def run_detection(exchange_name, ignored_symbols=None, whitelisted_symbols=None, max_cycle=10):
    last_prices = await get_exchange_last_prices(exchange_name, ignored_symbols or [], whitelisted_symbols)
    # default is the best opportunity for all cycles
    best_opportunity, best_profit = get_best_opportunity(last_prices, max_cycle=max_cycle)
    return best_opportunity, best_profit



    database.py

    import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

def init_db():
    """Initializes the database, creating tables if they don't exist."""
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS arbitrage_runs (
            id SERIAL PRIMARY KEY,
            exchange VARCHAR(255) NOT NULL,
            profit_percentage DOUBLE PRECISION NOT NULL,
            timestamp TIMESTAMP NOT NULL
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS trade_steps (
            id SERIAL PRIMARY KEY,
            run_id INTEGER NOT NULL REFERENCES arbitrage_runs(id) ON DELETE CASCADE,
            step_number INTEGER NOT NULL,
            market VARCHAR(255) NOT NULL,
            action VARCHAR(10) NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            base_currency VARCHAR(50) NOT NULL,
            quote_currency VARCHAR(50) NOT NULL
        );
        """))
        conn.commit()

def save_arbitrage_run(exchange, profit_percentage, opportunities):
    """Saves a complete arbitrage run and its trade steps to the database."""
    with engine.connect() as conn:
        result = conn.execute(
            text("INSERT INTO arbitrage_runs (exchange, profit_percentage, timestamp) VALUES (:exchange, :profit, :ts) RETURNING id;"),
            {"exchange": exchange, "profit": profit_percentage, "ts": datetime.now()}
        )
        run_id = result.scalar_one()
        
        for i, opp in enumerate(opportunities):
            conn.execute(
                text("""INSERT INTO trade_steps (run_id, step_number, market, action, price, base_currency, quote_currency)
                   VALUES (:run_id, :step, :market, :action, :price, :base, :quote);"""),
                {
                    "run_id": run_id,
                    "step": i + 1,
                    "market": f"{opp.symbol.base}/{opp.symbol.quote}",
                    "action": "BUY" if opp.reversed else "SELL",
                    "price": opp.last_price,
                    "base": opp.symbol.base,
                    "quote": opp.symbol.quote
                }
            )
        conn.commit()

def get_historical_profit_trend(exchange, limit=100, start_date=None, end_date=None):
    """Retrieves the profit trend for a given exchange from the database, with optional date filtering."""
    params = {"exchange": exchange, "limit": limit}
    
    # Base query
    query_str = """
    SELECT timestamp, profit_percentage 
    FROM arbitrage_runs 
    WHERE exchange = :exchange
    """
    
    # Append date filters if provided
    if start_date:
        query_str += " AND timestamp >= :start_date"
        params["start_date"] = start_date
    if end_date:
        # Add 1 day to the end_date to make the filter inclusive of the selected day
        query_str += " AND timestamp < :end_date + INTERVAL '1 day'"
        params["end_date"] = end_date
        
    query_str += " ORDER BY timestamp DESC LIMIT :limit;"
    
    query = text(query_str)
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
        
    return df.sort_values(by="timestamp")


    dashboard.py

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

# --- Asset Handling ---
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
    ''', unsafe_allow_html=True)

# --- Data Caching & Fetching ---
@st.cache_data(ttl=30)
def find_arbitrage_opportunities(exchange_name):
    try:
        opportunities, profit = asyncio.run(detector.run_detection(exchange_name))
        return opportunities, profit, datetime.now()
    except Exception as e:
        return None, None, datetime.now(), str(e)

# --- UI Components ---

def display_sidebar():
    with st.sidebar:
        st.title("🤖 Triangular Arbitrage")

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

        st.markdown("---")
        st.markdown("### 📊 Chart Controls")
        limit = st.slider("Recent Scans to Display", 50, 500, 100, 10)
        
        today = date.today()
        last_month = today - timedelta(days=30)
        start_date = st.date_input("Start Date", last_month)
        end_date = st.date_input("End Date", today)


        st.markdown("---")
        st.caption("Last updated:")
        last_updated_placeholder = st.empty()

    return exchange, auto_refresh, refresh_interval, limit, start_date, end_date, last_updated_placeholder

def display_historical_chart(exchange, limit, start_date, end_date):
    with st.expander("📈 View Profitability Trend", expanded=True):
        history_df = database.get_historical_profit_trend(exchange, limit, start_date, end_date)
        
        if not history_df.empty:
            fig = px.line(
                history_df, x='timestamp', y='profit_percentage',
                title=f'Profitability Over Time for {exchange.upper()}',
                labels={'timestamp': 'Time', 'profit_percentage': 'Profit %'}
            )
            
            # Add a marker for the most recent point
            last_point = history_df.iloc[-1]
            fig.add_scatter(
                x=[last_point['timestamp']], y=[last_point['profit_percentage']],
                mode='markers',
                marker=dict(color='#00FF41', size=10, symbol='diamond'),
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

def display_trade_sequence(opportunities):
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

    st.download_button(
        label="💾 Download Sequence as CSV",
        data=pd.DataFrame(trade_data_for_export).to_csv(index=False).encode("utf-8"),
        file_name=f"arbitrage_{st.session_state.exchange}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

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
    
    exchange, auto_refresh, refresh_interval, limit, start_date, end_date, last_updated_placeholder = display_sidebar()

    st.markdown('<div class="main-title">Arbitrage Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="exchange-subtitle">{exchange.upper()}</div>', unsafe_allow_html=True)

    with st.spinner(f"Scanning {exchange} for opportunities..."):
        fetch_result = find_arbitrage_opportunities(exchange)

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
        st.error(f"❌ Error connecting to {exchange}: {error_message}")
    elif opportunities:
        profit_percentage = (profit - 1) * 100
        database.save_arbitrage_run(exchange, profit_percentage, opportunities)

        st.metric(label="🎯 Est. Profit Opportunity", value=f"{profit_percentage:.4f}%")
        
        display_historical_chart(exchange, limit, start_date, end_date)
        
        st.markdown("---")
        display_trade_sequence(opportunities)
    else:
        st.success("✅ No profitable arbitrage opportunities detected at the moment.")
        display_historical_chart(exchange, limit, start_date, end_date)

    display_footer()

    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()


main.py

import asyncio

import octobot_commons.symbols as symbols
import octobot_commons.os_util as os_util

import triangular_arbitrage.detector as detector

if __name__ == "__main__":
    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # Windows handles asynchronous event loops
    
    benchmark = os_util.parse_boolean_environment_var("IS_BENCHMARKING", "False")
    if benchmark:
        import time

        s = time.perf_counter()

    # start arbitrage detection
    print("Scanning...")
    exchange_name = "binanceus"  # allow pickable exchange_id from https://github.com/ccxt/ccxt/wiki/manual#exchanges

    best_opportunities, best_profit = asyncio.run(detector.run_detection(exchange_name))


    def opportunity_symbol(opportunity):
        return symbols.parse_symbol(str(opportunity.symbol))


    def get_order_side(opportunity: detector.ShortTicker):
        return 'buy' if opportunity.reversed else 'sell'


    if best_opportunities is not None:
        # Display arbitrage detection result
        print("-------------------------------------------")
        total_profit_percentage = round((best_profit - 1) * 100, 5)
        print(f"New {total_profit_percentage}% {exchange_name} opportunity:")
        for i, opportunity in enumerate(best_opportunities):
            # Get the base and quote currencies
            base_currency = opportunity.symbol.base
            quote_currency = opportunity.symbol.quote

            # Format the output as below (real live example):
            # -------------------------------------------
            # New 2.33873% binanceus opportunity:
            # 1. buy DOGE with BTC at 552486.18785
            # 2. sell DOGE for USDT at 0.12232
            # 3. buy ETH with USDT at 0.00038
            # 4. buy ADA with ETH at 7570.02271
            # 5. sell ADA for USDC at 0.35000
            # 6. buy SOL with USDC at 0.00662
            # 7. sell SOL for BTC at 0.00226
            # -------------------------------------------
            order_side = get_order_side(opportunity)
            print(
                f"{i + 1}. {order_side} {base_currency} "
                f"{'with' if order_side == 'buy' else 'for'} "
                f"{quote_currency} at {opportunity.last_price:.5f}")
        print("-------------------------------------------")
    else:
        print("No opportunity detected")

    if benchmark:
        elapsed = time.perf_counter() - s
        print(f"{__file__} executed in {elapsed:0.2f} seconds.")