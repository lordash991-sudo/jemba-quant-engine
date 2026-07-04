from pathlib import Path

from jemba_core.database.sqlite_storage import SQLiteStorage
from jemba_core.database.candle_repository import CandleRepository
from jemba_core.ai.predictor import Predictor
from jemba_core.ai.confidence_engine import ConfidenceEngine
from jemba_core.ai.ranking_engine import RankingEngine
from jemba_core.portfolio.portfolio_manager import PortfolioManager


class QuantOrchestrator:

    def __init__(
        self,
        account_balance: float = 10000,
        min_confidence: float = 0.70
    ):
        self.storage = SQLiteStorage()
        self.repo = CandleRepository(self.storage)
        self.confidence_engine = ConfidenceEngine(min_confidence)
        self.ranking_engine = RankingEngine()
        self.portfolio = PortfolioManager(account_balance=account_balance)

    def model_path(self, symbol: str):
        safe_symbol = symbol.replace("-", "")
        return Path("models/trained") / f"{safe_symbol}_random_forest.pkl"

    def analyze_symbol(self, symbol: str, timeframe: str = "1h", limit: int = 300):
        model_file = self.model_path(symbol)

        if not model_file.exists():
            return None

        df = self.repo.load_candles(symbol, timeframe, limit)

        predictor = Predictor(model_file)
        prediction = predictor.predict(df)

        decision = self.confidence_engine.evaluate(prediction)
        decision["symbol"] = symbol
        decision["timeframe"] = timeframe

        return decision

    def scan(self, symbols, timeframe: str = "1h"):
        results = []

        for symbol in symbols:
            result = self.analyze_symbol(symbol, timeframe)

            if result is not None:
                results.append(result)

        return self.ranking_engine.rank(results)

    def best_opportunity(self, symbols, timeframe: str = "1h"):
        ranked = self.scan(symbols, timeframe)

        if not ranked:
            return None

        return ranked[0]
