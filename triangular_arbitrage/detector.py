# pylint: disable=W0702, C0325

import ccxt.async_support as ccxt
from typing import List, Tuple
from dataclasses import dataclass
import networkx as nx
import asyncio
from ccxt.base.errors import RateLimitExceeded, ExchangeError, NetworkError

import octobot_commons.symbols as symbols
import octobot_commons.constants as constants


@dataclass
class ShortTicker:
    symbol: symbols.Symbol
    last_price: float
    reversed: bool = False


async def fetch_tickers(exchange, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            return await exchange.fetch_tickers() if exchange.has['fetchTickers'] else []
        except (RateLimitExceeded, NetworkError) as e:
            retries += 1
            delay = 2 ** retries  # Exponential backoff
            print(f"Rate limit or network error: {e}. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
        except ExchangeError as e:
            print(f"Exchange error: {e}. Not retrying.")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Not retrying.")
            return []
    print(f"Failed to fetch tickers after {max_retries} retries.")
    return []


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


def get_best_opportunity(tickers: List[ShortTicker], max_cycle: int = 10, profit_threshold=1.025) -> Tuple[List[ShortTicker], float, List[Tuple[List[ShortTicker], float]]]:
    # Build a directed graph of currencies
    graph = nx.DiGraph()

    for ticker in tickers:
        if ticker.symbol is not None:
            graph.add_edge(ticker.symbol.base, ticker.symbol.quote, ticker=ticker)
            graph.add_edge(ticker.symbol.quote, ticker.symbol.base,
                           ticker=ShortTicker(symbols.Symbol(f"{ticker.symbol.quote}/{ticker.symbol.base}"),
                                              1 / ticker.last_price, reversed=True))

    profitable_cycles = []

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

        if profit > profit_threshold:
            # Correct the tickers for reversed trades before storing
            corrected_cycle = [
                ShortTicker(symbols.Symbol(f"{t.symbol.quote}/{t.symbol.base}"), 1 / t.last_price, reversed=True)
                if t.reversed else t
                for t in tickers_in_cycle
            ]
            profitable_cycles.append((corrected_cycle, profit))

    if not profitable_cycles:
        return None, 1, []

    # Sort by profit in descending order
    profitable_cycles.sort(key=lambda x: x[1], reverse=True)

    # The best one is the first in the sorted list
    best_cycle, best_profit = profitable_cycles[0]

    return best_cycle, best_profit, profitable_cycles


async def get_exchange_data(exchange_name, max_retries=3):
    exchange_class = getattr(ccxt, exchange_name)
    exchange = exchange_class()
    tickers = await fetch_tickers(exchange, max_retries)
    exchange_time = exchange.milliseconds()
    await exchange.close()
    return tickers, exchange_time


async def get_exchange_last_prices(exchange_name, ignored_symbols, whitelisted_symbols=None, max_retries=3):
    tickers, exchange_time = await get_exchange_data(exchange_name, max_retries)
    last_prices = get_last_prices(exchange_time, tickers, ignored_symbols, whitelisted_symbols)
    return last_prices


async def run_detection(exchange_name, ignored_symbols=None, whitelisted_symbols=None, max_cycle=10, max_retries=3):
    last_prices = await get_exchange_last_prices(exchange_name, ignored_symbols or [], whitelisted_symbols, max_retries)
    # default is the best opportunity for all cycles
    best_opportunity, best_profit, all_opportunities = get_best_opportunity(last_prices, max_cycle=max_cycle)
    return best_opportunity, best_profit, all_opportunities
