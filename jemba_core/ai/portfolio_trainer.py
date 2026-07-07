from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

from jemba_core.ai.feature_selector import FEATURES
from jemba_core.ai.label_generator import LabelGenerator
from jemba_core.database.candle_repository import CandleRepository
from jemba_core.database.sqlite_storage import SQLiteStorage
from jemba_core.features.feature_engine import FeatureEngine


class PortfolioTrainer:

    def __init__(self):
        self.storage = SQLiteStorage()
        self.repo = CandleRepository(self.storage)
        Path("models/trained").mkdir(parents=True, exist_ok=True)

    def symbols(self):
        query = "SELECT DISTINCT symbol FROM candles ORDER BY symbol"
        df = pd.read_sql(query, self.storage.engine)
        return df["symbol"].tolist()

    def prepare_data(self, symbol, timeframe="1h", limit=30000):
        df = self.repo.load_candles(symbol, timeframe, limit)

        df = FeatureEngine.generate(df)
        df = LabelGenerator.generate(df)

        df = df.dropna().reset_index(drop=True)

        return df

    def train_symbol(self, symbol):
        df = self.prepare_data(symbol)

        missing = [col for col in FEATURES if col not in df.columns]

        if missing:
            raise ValueError(f"Faltan features en {symbol}: {missing}")

        X = df[FEATURES]
        y = df["LABEL"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            shuffle=False
        )

        model = RandomForestClassifier(
            n_estimators=500,
            max_depth=20,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced"
        )

        model.fit(X_train, y_train)

        preds = model.predict(X_test)

        accuracy = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted")

        safe_symbol = symbol.replace("-", "")
        model_path = Path("models/trained") / f"{safe_symbol}_random_forest.pkl"

        joblib.dump(model, model_path)

        importance = pd.DataFrame({
            "feature": FEATURES,
            "importance": model.feature_importances_
        }).sort_values("importance", ascending=False)

        importance_path = Path("models/trained") / f"{safe_symbol}_feature_importance.csv"
        importance.to_csv(importance_path, index=False)

        return {
            "symbol": symbol,
            "rows": len(df),
            "features": len(FEATURES),
            "accuracy": round(accuracy, 4),
            "f1_score": round(f1, 4),
            "model": str(model_path),
            "importance": str(importance_path)
        }

    def train_all(self):
        results = []

        for symbol in self.symbols():
            print()
            print(f"Entrenando {symbol}...")

            result = self.train_symbol(symbol)

            print(result)

            results.append(result)

        report = pd.DataFrame(results)
        report.to_csv("models/trained/training_report.csv", index=False)

        return report
