from dataclasses import dataclass

import pandas as pd


@dataclass
class PO3Trade:
    symbol: str
    timeframe: str
    direction: str
    entry_index: int
    entry_price: float
    stop_loss: float
    take_profit: float
    exit_index: int | None = None
    exit_price: float | None = None
    result: str = "OPEN"


class PO3Engine:

    def __init__(
        self,
        accumulation_length: int = 40,
        accumulation_atr_mult: float = 5.0,
        manipulation_atr_mult: float = 0.6,
        accumulation_expand_mult: float = 0.5,
        rr: float = 0.86,
        sl_atr_mult: float = 5.0,
    ):
        self.accumulation_length = accumulation_length
        self.accumulation_atr_mult = accumulation_atr_mult
        self.manipulation_atr_mult = manipulation_atr_mult
        self.accumulation_expand_mult = accumulation_expand_mult
        self.rr = rr
        self.sl_atr_mult = sl_atr_mult

    def detect(self, df: pd.DataFrame, symbol: str, timeframe: str) -> list[PO3Trade]:
        df = df.copy().reset_index(drop=True)

        if "ATR" not in df.columns:
            raise ValueError("El DataFrame debe tener columna ATR. Usa FeatureEngine.generate(df) primero.")

        trades = []
        active_trade = None

        state = "WAITING_ACCUMULATION"

        acc_top = None
        acc_bottom = None
        acc_end_top = None
        acc_end_bottom = None
        acc_end_index = None

        manipulation_direction = None

        for i in range(self.accumulation_length, len(df)):

            row = df.iloc[i]
            atr = row["ATR"]

            if pd.isna(atr):
                continue

            if active_trade is not None and active_trade.result == "OPEN":
                active_trade = self._update_trade(active_trade, df, i)
                if active_trade.result != "OPEN":
                    trades.append(active_trade)
                    active_trade = None
                    state = "WAITING_ACCUMULATION"
                continue

            window = df.iloc[i - self.accumulation_length:i]

            highest_acc = window["high"].max()
            lowest_acc = window["low"].min()

            if state == "WAITING_ACCUMULATION":
                if (highest_acc - lowest_acc) <= atr * self.accumulation_atr_mult:
                    acc_top = highest_acc + atr * self.accumulation_expand_mult
                    acc_bottom = lowest_acc - atr * self.accumulation_expand_mult
                    acc_end_index = i
                    state = "WAITING_ACCUMULATION_END"

            elif state == "WAITING_ACCUMULATION_END":
                if row["high"] > acc_top or row["low"] < acc_bottom:
                    acc_end_top = row["high"]
                    acc_end_bottom = row["low"]
                    acc_end_index = i
                    state = "WAITING_MANIPULATION"
                else:
                    acc_end_index = i

            elif state == "WAITING_MANIPULATION":
                if i > acc_end_index:

                    if row["high"] > acc_top + atr * self.manipulation_atr_mult:
                        manipulation_direction = "BULLISH"
                        state = "WAITING_DISTRIBUTION"

                    elif row["low"] < acc_bottom - atr * self.manipulation_atr_mult:
                        manipulation_direction = "BEARISH"
                        state = "WAITING_DISTRIBUTION"

            elif state == "WAITING_DISTRIBUTION":

                entry_price = float(row["close"])

                if manipulation_direction == "BEARISH":
                    direction = "BUY"
                    stop_loss = entry_price - atr * self.sl_atr_mult
                    take_profit = entry_price + abs(entry_price - stop_loss) * self.rr

                else:
                    direction = "SELL"
                    stop_loss = entry_price + atr * self.sl_atr_mult
                    take_profit = entry_price - abs(entry_price - stop_loss) * self.rr

                active_trade = PO3Trade(
                    symbol=symbol,
                    timeframe=timeframe,
                    direction=direction,
                    entry_index=i,
                    entry_price=round(entry_price, 6),
                    stop_loss=round(float(stop_loss), 6),
                    take_profit=round(float(take_profit), 6),
                )

                state = "TRADE_OPEN"

        return trades

    def _update_trade(self, trade: PO3Trade, df: pd.DataFrame, i: int) -> PO3Trade:
        row = df.iloc[i]

        high = float(row["high"])
        low = float(row["low"])

        if trade.direction == "BUY":

            if low <= trade.stop_loss:
                trade.exit_index = i
                trade.exit_price = trade.stop_loss
                trade.result = "SL"

            elif high >= trade.take_profit:
                trade.exit_index = i
                trade.exit_price = trade.take_profit
                trade.result = "TP"

        elif trade.direction == "SELL":

            if high >= trade.stop_loss:
                trade.exit_index = i
                trade.exit_price = trade.stop_loss
                trade.result = "SL"

            elif low <= trade.take_profit:
                trade.exit_index = i
                trade.exit_price = trade.take_profit
                trade.result = "TP"

        return trade
