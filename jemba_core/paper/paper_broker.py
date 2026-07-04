from jemba_core.paper.paper_position import PaperPosition


class PaperBroker:

    def __init__(self, account):
        self.account = account

    def execute(self, signal):
        if signal is None:
            return None

        if self.account.has_open_position():
            return None

        position = PaperPosition(
            symbol=signal.symbol,
            action=signal.action,
            entry=signal.entry,
            quantity=signal.quantity,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit
        )

        self.account.open(position)

        return position

    def update(self, candle):
        if not self.account.has_open_position():
            return None

        position = self.account.open_position

        high = candle["high"]
        low = candle["low"]

        if position.action == "BUY":
            if low <= position.stop_loss:
                return self.account.close(position.stop_loss)

            if high >= position.take_profit:
                return self.account.close(position.take_profit)

        if position.action == "SELL":
            if high >= position.stop_loss:
                return self.account.close(position.stop_loss)

            if low <= position.take_profit:
                return self.account.close(position.take_profit)

        return None
