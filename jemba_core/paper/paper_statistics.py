class PaperStatistics:

    @staticmethod
    def calculate(trades):
        total_trades = len(trades)

        if total_trades == 0:
            return {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "gross_profit": 0.0,
                "gross_loss": 0.0,
                "profit_factor": 0.0,
                "expectancy": 0.0,
            }

        pnls = [float(t.get("pnl", 0.0)) for t in trades]

        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))

        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        win_rate = len(wins) / total_trades
        expectancy = sum(pnls) / total_trades

        return {
            "total_trades": total_trades,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 4),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "profit_factor": round(profit_factor, 4),
            "expectancy": round(expectancy, 4),
        }
