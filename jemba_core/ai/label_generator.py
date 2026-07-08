import pandas as pd


class LabelGenerator:
    def generate(
        self,
        df: pd.DataFrame,
        future_periods: int = 3,
        threshold: float = 0.002,
    ) -> pd.DataFrame:
        data = df.copy()
        future_return = data["close"].shift(-future_periods) / data["close"] - 1

        data["label"] = 0
        data.loc[future_return > threshold, "label"] = 1
        data.loc[future_return < -threshold, "label"] = -1

        return data.dropna().reset_index(drop=True)
