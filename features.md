# Triangular Arbitrage Detector

## Introduction

This document provides a comprehensive overview of the Triangular Arbitrage Detector, a Python-based tool designed to identify arbitrage opportunities across various cryptocurrency exchanges. The tool leverages the `ccxt` library to fetch real-time market data and `networkx` to model and analyze currency relationships for profitable trading cycles.

## Features

- **Multi-Exchange Support:** Powered by the `ccxt` library, it can be configured to work with any exchange that `ccxt` supports.
- **Arbitrage Cycle Detection:** Identifies not only simple triangular arbitrage (3 currencies) but also more complex cycles with up to 10 currency pairs.
- **Graph-Based Analysis:** Utilizes the `networkx` library to represent currency pairs as a directed graph, allowing for efficient cycle detection.
- **Profit Calculation:** Calculates the potential profit from an arbitrage cycle and presents the most profitable opportunity.
- **Symbol Filtering:** Allows for whitelisting and ignoring specific trading symbols to focus the search on relevant pairs.
- **Stale Ticker Filtering:** Automatically filters out delisted or inactive trading pairs to ensure the reliability of detected opportunities.
- **Reversed Pair Handling:** Intelligently handles both direct (e.g., BTC/USDT) and reverse (e.g., USDT/BTC) trading possibilities by calculating inverse prices.
- **Clear Output:** Presents the detected arbitrage opportunity as a clear, step-by-step list of trades.
- **Benchmarking:** Includes an optional mode to measure the script's execution time for performance analysis.

## How It Works

The arbitrage detection process can be broken down into the following steps:

1.  **Data Fetching:** The script initiates a connection to the specified exchange using `ccxt` and fetches the latest ticker data for all available trading pairs.

2.  **Data Cleaning and Preparation:**
    *   The raw ticker data is filtered to remove any pairs that have not been updated recently (delisted or stale).
    *   The relevant information (symbol and last price) is extracted and stored in a custom `ShortTicker` data structure.
    *   Any user-defined ignored symbols are removed from consideration.

3.  **Graph Construction:**
    *   A directed graph is created using the `networkx` library, where each currency (e.g., BTC, ETH, USDT) is a node.
    *   For each trading pair, two directed edges are added to the graph:
        *   A forward edge representing a "sell" (e.g., from BTC to USDT). The weight of this edge is the last price.
        *   A reverse edge representing a "buy" (e.g., from USDT to BTC). The weight is calculated as `1 / last_price`.

4.  **Cycle and Profit Analysis:**
    *   The algorithm searches the graph for all simple cycles (paths that start and end at the same currency).
    *   For each detected cycle, it calculates the potential profit by multiplying the weights (prices) of all edges in the cycle.
    *   If the final product is greater than 1, it signifies a profitable arbitrage opportunity.

5.  **Result Presentation:**
    *   The script identifies the cycle with the highest profit.
    *   If a profitable opportunity is found, it is displayed to the user as a numbered list of buy/sell actions, showing the currencies involved and the exchange rate at each step.

## Usage

The primary entry point for the tool is the `main.py` script.

-   **Configuration:** To change the target exchange, modify the `exchange_name` variable in `main.py`.
-   **Execution:** Run the script from your terminal:
    ```bash
    python main.py
    ```
-   **Output:** The script will print the best-detected arbitrage opportunity to the console, including the total percentage profit and the sequence of trades. If no opportunity is found, it will indicate so.
