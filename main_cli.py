import asyncio
from queue import Queue, Empty
import time
import pandas as pd
from streammarket import StreamMarket
from scraper import get_top_tokens
import logging
import threading
import typer
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def addData(df: pd.DataFrame, data):
    # update df dataframe with new data
    indf = df.copy()
    new_data = pd.DataFrame([data]).set_index("name")
    if indf.empty:
        indf = new_data
    else:
        if new_data.index[0] in indf.index:
            indf.update(new_data)
        else:
            indf = pd.concat([indf, new_data])
    return indf

def runner(
    token: Optional[str] = typer.Option(None, help="Comma-separated list of tokens (e.g., BTC,ETH). If not provided, fetches top tokens from CoinMarketCap."), 
    outputfile: str = "output.csv"
):
    """
    Stream cryptocurrency prices from CoinMarketCap WebSocket.
    """
    # If no tokens provided, scrape from CoinMarketCap
    if token is None:
        logger.info("No tokens specified, fetching from CoinMarketCap...")
        tokens = get_top_tokens(limit=20)
        logger.info(f"Using top {len(tokens)} tokens: {', '.join(tokens)}")
    else:
        tokens = token.split(",")
        logger.info(f"Using specified tokens: {', '.join(tokens)}")
    
    logger.info("Call market stream")
    queue = Queue()
    market = StreamMarket(queue, tokens)
    th = threading.Thread(target=lambda: asyncio.run(market.getMarket()), name="MarketStream")
    th.daemon = True
    th.start()
    try:
        for _ in range(5):
            if th.is_alive():
                break
            time.sleep(1)
        else:
            logger.error("MarketStream thread failed to start")
            return
        logger.info("Thread is alive, let's get data")

        df = pd.DataFrame()
        while th.is_alive() or not queue.empty():
            try:
                data = queue.get(timeout=2)
            except Empty:
                continue
            logger.info(f"Get data: {data}")
            df = addData(df, data)
            print(df)
            df.to_csv(outputfile)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")

    logger.info("The End")

if __name__ == "__main__":
    typer.run(runner)