class PipelineEngine:

    def __init__(
        self,
        feature_engine=None,
        predictor=None,
        confidence_engine=None,
        signal_engine=None,
        ranking_engine=None,
        risk_engine=None,
        portfolio_manager=None,
        execution_engine=None,
    ):
        self.feature_engine = feature_engine
        self.predictor = predictor
        self.confidence_engine = confidence_engine
        self.signal_engine = signal_engine
        self.ranking_engine = ranking_engine
        self.risk_engine = risk_engine
        self.portfolio_manager = portfolio_manager
        self.execution_engine = execution_engine

    def execute(self, market=None):
        data = market

        if self.feature_engine:
            data = self.feature_engine.compute(data)

        if self.predictor:
            data = self.predictor.predict(data)

        if self.confidence_engine:
            data = self.confidence_engine.evaluate(data)

        if self.signal_engine:
            data = self.signal_engine.generate(data)

        if self.ranking_engine:
            data = self.ranking_engine.rank(data)

        if self.risk_engine:
            data = self.risk_engine.apply(data)

        if self.portfolio_manager:
            data = self.portfolio_manager.update(data)

        if self.execution_engine:
            data = self.execution_engine.execute(data)

        return data
