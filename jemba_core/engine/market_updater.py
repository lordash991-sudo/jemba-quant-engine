class MarketUpdater:

    def __init__(
        self,
        market_provider=None,
        candle_repository=None,
        event_bus=None,
        scheduler=None,
        symbols=None,
        timeframe="1h",
    ):
        self.market_provider = market_provider
        self.candle_repository = candle_repository
        self.event_bus = event_bus
        self.scheduler = scheduler
        self.symbols = symbols or []
        self.timeframe = timeframe

    def update_symbol(self, symbol, timeframe=None):
        timeframe = timeframe or self.timeframe

        try:
            candle = self.market_provider.get_latest(
                symbol=symbol,
                timeframe=timeframe,
            )

            if candle is None:
                return False

            saved = self.candle_repository.save(candle)

            if self.event_bus is not None:
                self.event_bus.publish({
                    "event_type": "MarketUpdated",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "candle": candle,
                })

            return bool(saved)

        except Exception:
            return False

    def update_all(self, symbols=None, timeframe=None):
        symbols = symbols or self.symbols
        results = {}

        for symbol in symbols:
            results[symbol] = self.update_symbol(symbol, timeframe)

        return results

    def run_once(self):
        return self.update_all()

    def run(self):
        while self.scheduler.should_continue():
            self.run_once()
            self.scheduler.sleep()
