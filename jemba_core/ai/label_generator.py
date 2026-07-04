import pandas as pd


class LabelGenerator:

    @staticmethod
    def generate(
        df: pd.DataFrame,
        tp=0.03,
        sl=0.015,
        lookahead=24
    ):

        labels = []

        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values

        total = len(df)

        for i in range(total):

            entry = closes[i]

            take_profit = entry * (1 + tp)
            stop_loss = entry * (1 - sl)

            label = 0

            last = min(i + lookahead, total - 1)

            for j in range(i + 1, last + 1):

                if highs[j] >= take_profit:
                    label = 1
                    break

                if lows[j] <= stop_loss:
                    label = -1
                    break

            labels.append(label)

        df = df.copy()
        df["LABEL"] = labels

        return df
