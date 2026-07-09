from __future__ import annotations

import numpy as np
import pandas as pd


class VolatilityFeatures:
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()

        high = data["high"]
        low = data["low"]
        close = data["close"]
        open_ = data["open"]

        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()

        data["true_range"] = pd.concat(
            [tr1, tr2, tr3],
            axis=1,
        ).max(axis=1)

        data["atr_14"] = data["true_range"].rolling(14).mean()

        data["atr_pct"] = data["atr_14"] / close

        data["range_pct"] = (high - low) / close

        body = (close - open_).abs()

        data["body_pct"] = body / close

        upper = high - pd.concat([open_, close], axis=1).max(axis=1)

        lower = pd.concat([open_, close], axis=1).min(axis=1) - low

        data["upper_wick_pct"] = upper / close
        data["lower_wick_pct"] = lower / close

        returns = np.log(close / close.shift())

        data["rolling_std_20"] = returns.rolling(20).std()

        data["historical_vol_20"] = data["rolling_std_20"] * np.sqrt(252)

        data["realized_vol_20"] = returns.pow(2).rolling(20).sum().pow(0.5)

        return data
