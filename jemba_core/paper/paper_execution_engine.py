class PaperExecutionEngine:

    def __init__(
        self,
        broker_executor,
        paper_engine,
        reporter,
        statistics,
    ):
        self.broker_executor = broker_executor
        self.paper_engine = paper_engine
        self.reporter = reporter
        self.statistics = statistics

    def execute(self, opportunity):
        if opportunity is None:
            return None

        order = self.broker_executor.execute(opportunity)

        if order is None:
            return None

        if hasattr(self.paper_engine, "register"):
            self.paper_engine.register(order)

        if hasattr(self.statistics, "update"):
            self.statistics.update(order)

        if hasattr(self.reporter, "record"):
            self.reporter.record(order)

        return order
