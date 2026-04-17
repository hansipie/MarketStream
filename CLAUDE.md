# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MarketStream is a Python application that streams real-time cryptocurrency price data from CoinMarketCap's WebSocket API. It uses websockets, multithreading, and queues to fetch and display market data. There are two frontends: a Streamlit web UI and a CLI.

## Commands

### Install dependencies
```bash
uv sync
```

### Run the Streamlit web UI
```bash
uv run streamlit run app.py
```

L'application récupère automatiquement les top 20 tokens depuis la homepage de CoinMarketCap au démarrage.

### Run the CLI
```bash
uv run python main_cli.py --token "BTC,ETH" --outputfile output.csv
```

Si vous ne spécifiez pas `--token`, l'application récupère automatiquement les top 20 tokens depuis la homepage de CoinMarketCap :
```bash
uv run python main_cli.py
```


## Architecture

The app has a producer/consumer architecture with three layers:

1. **`streammarket.py` — `StreamMarket` class (producer):** Connects to `wss://push.coinmarketcap.com` via websocket, subscribes to price updates for specified coins, parses incoming messages, and puts structured `{name, symbol, timestamp, price}` dicts onto a `Queue`. Uses `data/cmc_idmap.json` to map coin symbols (e.g. "BTC") to CoinMarketCap numeric IDs.

2. **`app.py` — Streamlit frontend (consumer):** Launches the StreamMarket websocket in a daemon thread, polls the queue every second via `@st.experimental_fragment(run_every=1)`, and accumulates data into a `st.session_state` DataFrame displayed as a live table. Automatically scrapes the top tokens from CoinMarketCap on first load.

3. **`main_cli.py` — CLI frontend (consumer):** Uses Typer. Same daemon-thread pattern but prints the DataFrame to stdout and saves to CSV on each update. Can use auto-scraped tokens or manually specified ones via `--token`.

4. **`scraper.py` — Token scraper:** Scrapes the CoinMarketCap homepage to dynamically fetch the top tokens currently displayed. Used by both frontends when no explicit token list is provided.

### Key patterns
- The websocket runs in a background daemon thread via `threading.Thread` + `asyncio.run()`, communicating with the main thread through `queue.Queue`.
- In the Streamlit app, the thread is deduplicated by checking `threading.enumerate()` for a thread named "MarketStream".
- DataFrame updates use an upsert pattern: update existing rows by coin name index, or concat new rows.
