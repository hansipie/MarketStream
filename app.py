import streamlit as st
import pandas as pd
import threading
import time
import logging
import asyncio
from queue import Queue

from streammarket import StreamMarket
from scraper import get_top_tokens

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()
if "queue" not in st.session_state:
    st.session_state.queue = Queue()
if "tokens" not in st.session_state:
    # Scrape tokens on first load
    logger.info("Fetching tokens from CoinMarketCap...")
    st.session_state.tokens = get_top_tokens(limit=20)
    logger.info(f"Using tokens: {st.session_state.tokens}")

st.title("Market Stream")
st.caption(f"Tracking {len(st.session_state.tokens)} tokens: {', '.join(st.session_state.tokens[:10])}{'...' if len(st.session_state.tokens) > 10 else ''}")

def threadLauncher():
    for thread in threading.enumerate():
        if thread.name == "MarketStream":
            logger.info("Thread is already running")
            break
    else:
        market = StreamMarket(st.session_state.queue, st.session_state.tokens)
        th = threading.Thread(target=lambda: asyncio.run(market.getMarket()), name="MarketStream")
        th.daemon = True
        th.start()
        for _ in range(5):
            if th.is_alive():
                break
            time.sleep(1)
        else:
            logger.error("MarketStream thread failed to start")
            return
        logger.info("Thread is alive, let's get data")


def addData(data):
    logger.debug(f"Data to add: {data}")
    new_data = pd.DataFrame([data]).set_index("name")
    if st.session_state.data.empty:
        st.session_state.data = new_data
    else:
        if new_data.index[0] in st.session_state.data.index:
            st.session_state.data.update(new_data)
        else:
            st.session_state.data = pd.concat([st.session_state.data, new_data])

@st.fragment(run_every=1)
def updateDataframe():
    try:
        queue = st.session_state.queue
        while not queue.empty():
            logger.debug(f"Queue size: {queue.qsize()}")
            addData(queue.get_nowait())
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.debug("Dataframe updated")
        st.dataframe(st.session_state.data, use_container_width=True)
    
threadLauncher()
updateDataframe()
