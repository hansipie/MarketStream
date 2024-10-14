import asyncio
from queue import Queue
import time
import pandas as pd
from streammarket import StreamMarket
import logging
import threading
import typer

dbg_lvl = logging.INFO
logger = logging.getLogger()
logger.setLevel(dbg_lvl)
handler = logging.StreamHandler()
handler.setLevel(dbg_lvl)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

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

def runnner(token: str = "BTC,ETH", ouputfile: str = "output.csv"):
    logger.info("Call market stream")
    queue = Queue()
    market = StreamMarket(queue, token.split(","))
    th = threading.Thread(target=lambda: asyncio.run(market.getMarket()))
    th.daemon = True
    th.start()
    try:
        while not th.is_alive():
            logger.info("Thread is not alive, let's wait a bit")
            time.sleep(1)
        logger.info("Thread is alive, let's get data")

        df = pd.DataFrame()
        while th.is_alive() or not queue.empty():
            data = queue.get()
            logger.info(f"Get data: {data}")
            df = addData(df, data)
            print(df)
            df.to_csv(ouputfile)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")

    logger.info("The End")

if __name__ == "__main__":
    typer.run(runnner)