import math


class Metrics:
    @staticmethod
    def win_rate(trades):
        if not trades:
            return 0.0
        wins = sum(1 for trade in trades if trade.pnl > 0)
        return wins / len(trades)

    @staticmethod
    def profit_factor(trades):
        gross_profit = sum(trade.pnl for trade in trades if trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in trades if trade.pnl < 0))

        if gross_loss == 0:
            return float("inf")

        return gross_profit / gross_loss

    @staticmethod
    def average_win(trades):
        wins = [trade.pnl for trade in trades if trade.pnl > 0]
        if not wins:
            return 0.0
        return sum(wins) / len(wins)

    @staticmethod
    def average_loss(trades):
        losses = [trade.pnl for trade in trades if trade.pnl < 0]
        if not losses:
            return 0.0
        return sum(losses) / len(losses)

    @staticmethod
    def expectancy(trades):
        win_rate = Metrics.win_rate(trades)
        avg_win = Metrics.average_win(trades)
        avg_loss = abs(Metrics.average_loss(trades))

        return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    @staticmethod
    def max_drawdown(equity):
        if not equity:
            return 0.0

        peak = equity[0]
        max_dd = 0.0

        for value in equity:
            peak = max(peak, value)
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)

        return max_dd

    @staticmethod
    def sharpe_ratio(trades):
        if len(trades) < 2:
            return 0.0

        returns = [trade.pnl_percent / 100 for trade in trades]
        avg_return = sum(returns) / len(returns)

        variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return 0.0

        return avg_return / std_dev
