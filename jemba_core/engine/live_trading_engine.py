class LiveTradingEngine:
    def __init__(
        self,
        market_provider,
        pipeline_engine,
        execution_engine,
        scheduler,
        symbols,
        timeframe="1h",
    ):
        self.market_provider = market_provider
        self.pipeline_engine = pipeline_engine
        self.execution_engine = execution_engine
        self.scheduler = scheduler
        self.symbols = list(symbols)
        self.timeframe = timeframe

    def run_once(self):
        for symbol in self.symbols:
            candles = self.market_provider.get_candles(
                symbol=symbol,
                timeframe=self.timeframe,
            )

            if candles is None:
                continue

            opportunity = self.pipeline_engine.process(
                symbol=symbol,
                timeframe=self.timeframe,
                candles=candles,
            )

            if opportunity is None:
                continue

            self.execution_engine.execute(opportunity)

    def run(self):
        while self.scheduler.should_continue():
            self.run_once()
            self.scheduler.sleep()
