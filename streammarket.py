import asyncio
import json
import websockets
from queue import Queue
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class StreamMarket:

    def __init__(self, queue: Queue, symbols: list[str] | None = None):
        idmap = self.__loadIDMap()
        self.__by_id = {item["id"]: item for item in idmap["data"]}
        self.__by_symbol = {}
        for item in sorted(idmap["data"], key=lambda x: x["rank"]):
            if item["symbol"] not in self.__by_symbol:
                self.__by_symbol[item["symbol"]] = item["id"]
        self.__queue = queue
        self.__symbols = self.__makeSymbolsString(symbols or ["BTC", "ETH", "SOL"])

    def __loadIDMap(self):
        with open(Path(__file__).parent / "data" / "cmc_idmap.json", encoding="UTF-8") as f:
            idmap = json.load(f)
        return idmap

    def __getCoinName(self, coin_id: int) -> str:
        return self.__by_id.get(coin_id, {}).get("name", "")

    def __getCoinSymbol(self, coin_id: int) -> str:
        return self.__by_id.get(coin_id, {}).get("symbol", "")

    def __getCoinID(self, symbol: str) -> list[int]:
        coin_id = self.__by_symbol.get(symbol)
        return [coin_id] if coin_id is not None else []
    
    def __makeSymbolsString(self, symbols: list[str]) -> str:
        if not symbols:
            return ""
        ids = []
        for symbol in symbols:
            found = self.__getCoinID(symbol)
            if not found:
                logger.warning(f"Symbol not found in idmap: {symbol}")
            ids.extend(found)
        str_ids = [str(i) for i in ids]
        logger.debug(f"Symbols string: {','.join(str_ids)}")
        return ",".join(str_ids)
    
    async def getMarket(self):
        logger.info("Starting market stream")
        uri = "wss://push.coinmarketcap.com/ws?device=web&client_source=home_page"
        payload = {
            "method": "RSUBSCRIPTION",
            "params": [
                "main-site@crypto_price_5s@{}@normal",
                self.__symbols,
            ],
        }
        delay = 1
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    delay = 1
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
                            coin_id = data["d"]["id"]
                            name = self.__getCoinName(coin_id)
                            symbol = self.__getCoinSymbol(coin_id)
                            if not name:
                                logger.warning(f"Unknown coin id from websocket: {coin_id}")
                                continue
                            coin_data = {
                                "name": name,
                                "symbol": symbol,
                                "timestamp": unix_timestamp,
                                "price": price,
                            }
                            logger.debug(f"Put new data: {coin_data}")
                            self.__queue.put(coin_data)
                        except KeyError as e:
                            logger.warning(f"Error parsing message: {e}")
            except KeyboardInterrupt:
                logger.info("Stopping market stream")
                return
            except Exception as e:
                logger.error(f"Connection lost: {e}. Reconnecting in {delay}s...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, 60)
