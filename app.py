import asyncio
from queue import Queue
import time
import pandas as pd
from streammarket import StreamMarket
import logging
import threading

dbg_lvl = logging.INFO
logger = logging.getLogger()
logger.setLevel(dbg_lvl)
handler = logging.StreamHandler()
handler.setLevel(dbg_lvl)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# if "data" not in st.session_state:
#     st.session_state.data = pd.DataFrame()


def addData(df: pd.DataFrame, data):
    # update df dataframe with new data
    indf = pd.DataFrame(df)
    new_data = pd.DataFrame(data)
    new_data = new_data.set_index("name")
    if indf.empty:
        indf = new_data
    else:
        if new_data.index[0] in indf.index:
            indf.update(new_data)
        else:
            indf = pd.concat([indf, new_data])
    return indf

logger.info("Call market stream")
thStopEvent = threading.Event()
queue = Queue()
market = StreamMarket(queue, thStopEvent)
th = threading.Thread(target=lambda: asyncio.run(market.getMarket()))
th.start()
try:
    while not th.is_alive():
        logger.info("Thread is not alive, let's wait a bit")
        time.sleep(1)
    logger.info("Thread is alive, let's get data")

    df = pd.DataFrame()
    while th.is_alive() or not market.queue.empty():
        data = market.queue.get()
        logger.info(f"Get data: {data}")
        df = addData(df, data)
        print(df)
except KeyboardInterrupt:
    logger.info("KeyboardInterrupt")
    thStopEvent.set()
    th.join()

logger.info("The End")