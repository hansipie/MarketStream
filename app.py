import streamlit as st
import pandas as pd
import threading
import time
import logging
import asyncio
from queue import Queue

from streammarket import StreamMarket

dbg_lvl = logging.DEBUG
logger = logging.getLogger()
logger.setLevel(dbg_lvl)
handler = logging.StreamHandler()
handler.setLevel(dbg_lvl)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()
if "queue" not in st.session_state:
    st.session_state.queue = Queue()

st.title("Market Stream")

def threadLauncher():
    for thread in threading.enumerate():
        if thread.name == "MarketStream":
            logger.info("Thread is already running")
            break
    else:
        market = StreamMarket(st.session_state.queue)
        th = threading.Thread(target=lambda: asyncio.run(market.getMarket()), name="MarketStream")
        th.daemon = True
        th.start()
        while not th.is_alive():
            logger.info("Thread is not alive, let's wait a bit")
            time.sleep(1)
        logger.info("Thread is alive, let's get data")


def addData(data):
    # update df dataframe with new data
    new_data = pd.DataFrame(data).set_index("name")
    if st.session_state.data.empty:
        st.session_state.data = new_data
    else:
        if new_data.index[0] in st.session_state.data.index:
            st.session_state.data.update(new_data)
        else:
            st.session_state.data = pd.concat([st.session_state.data, new_data])

@st.experimental_fragment(run_every=1)
def updateDataframe():
    try:
        queue = st.session_state.queue
        if not queue.empty():
            logger.debug(f"Queue size: {queue.qsize()}")
            addData(queue.get())
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.debug("Dataframe updated")
        st.dataframe(st.session_state.data)
    
threadLauncher()
updateDataframe()



