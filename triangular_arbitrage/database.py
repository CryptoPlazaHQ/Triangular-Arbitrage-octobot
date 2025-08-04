import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

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

def get_historical_profit_trend(exchange, limit=100):
    """Retrieves the profit trend for a given exchange from the database."""
    query = text("""
    SELECT timestamp, profit_percentage 
    FROM arbitrage_runs 
    WHERE exchange = :exchange
    ORDER BY timestamp DESC
    LIMIT :limit;
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"exchange": exchange, "limit": limit})
    return df.sort_values(by="timestamp")