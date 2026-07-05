import time
from datetime import datetime

from jemba_core.engine.market_updater import MarketUpdater
from jemba_core.engine.live_engine import LiveEngine


class Scheduler:

    def __init__(self):

        self.market = MarketUpdater()

        self.engine = LiveEngine()

    def cycle(self, symbol="BTC-USDT", timeframe="1h"):

        print("=" * 60)

        print(datetime.utcnow())

        print("ACTUALIZANDO MERCADO...")

        updated = self.market.update(symbol, timeframe)

        print("UPDATED:", updated)

        print()

        print("EJECUTANDO LIVE ENGINE")

        self.engine.cycle()

        print("=" * 60)

    def run(self, symbol="BTC-USDT", timeframe="1h", seconds=60):

        while True:

            self.cycle(symbol, timeframe)

            time.sleep(seconds)