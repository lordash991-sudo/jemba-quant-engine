from pathlib import Path
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


class Trainer:

    def __init__(self):

        self.features = [
            "EMA20",
            "EMA50",
            "ATR",
            "BODY",
            "BULLISH",
            "BEARISH",
        ]

    def train(self, df):

        X = df[self.features]

        y = df["LABEL"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            shuffle=False
        )

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        print(classification_report(y_test, predictions))

        Path("models/trained").mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(
            model,
            "models/trained/random_forest.pkl"
        )

        return model
