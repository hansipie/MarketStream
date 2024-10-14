import json
import websockets
from queue import Queue
import logging
from threading import Event

logger = logging.getLogger(__name__)

class StreamMarket:

    def __init__(self, queue: Queue, symbols: list = ["BTC", "ETH"]):
        self.__idmap = self.__loadIDMap()
        self.__queue = queue
        self.__symbols = self.__makeSymbolsString(symbols)
        pass

    def __loadIDMap(self):
        idmap = json.loads(open("./data/cmc_idmap.json", encoding="UTF-8").read())
        return idmap

    def __getCoinName(self, id: int):
        return [item["name"] for item in self.__idmap["data"] if item["id"] == id]
    
    def __getCoinSymbol(self, id: int):
        return [item["symbol"] for item in self.__idmap["data"] if item["id"] == id]
    
    def __getCoinID(self, symbol: str):
        return [item["id"] for item in self.__idmap["data"] if item["symbol"] == symbol]
    
    def __makeSymbolsString(self, symbols: list) -> str:
        if not symbols:
            return ""
        list = []
        for symbol in symbols:
            ids = self.__getCoinID(symbol)
            list.extend(ids)
        str_ids = [str(id) for id in list]
        logger.debug(f"Symbols string: {','.join(str_ids)}")
        return ",".join(str_ids)
    
    async def getMarket(self):
        logger.info("Starting market stream")
        uri = "wss://push.coinmarketcap.com/ws?device=web&client_source=home_page"
        async with websockets.connect(uri) as websocket:
            payload = {
                "method": "RSUBSCRIPTION",
                "params": [
                    "main-site@crypto_price_5s@{}@normal",
                    self.__symbols,
                ],
            }
            try:
                await websocket.send(json.dumps(payload))
                while True:
                    message = await websocket.recv()
                    logger.debug(f"Get new message: {message}")
                    data = json.loads(message)
                    if 't' not in data:
                        logger.debug(f"Skip message: {data}")
                        continue
                    try:
                        unix_timestamp = int(data["t"])
                        price = float(data["d"]["p"])
                        coin_data = {
                            "name": self.__getCoinName(data["d"]["id"]),
                            "symbol": self.__getCoinSymbol(data["d"]["id"]),
                            "timestamp": unix_timestamp,
                            "price": price,
                        }
                        logger.debug(f"Put new data: {coin_data}")
                        self.__queue.put(coin_data)
                    except KeyError as e:
                        logger.warning(f"Error parsing message: {e}")
                        pass
            except websockets.exceptions.ConnectionClosedError as e:
                logger.error(f"Connection closed: {e}")
                pass 
            except KeyboardInterrupt:
                logger.info("Stopping market stream")
                pass
            except Exception as e:
                logger.error(f"Error: {e}")
                pass
