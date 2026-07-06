from jemba_core.paper.paper_account import PaperAccount
from jemba_core.paper.paper_position import PaperPosition


class PaperEngine:

    def __init__(self, account=None):

        self.account = account or PaperAccount()

        self.positions = []

        self.closed_positions = []

    def open_position(self, position: PaperPosition):

        self.positions.append(position)

        return position

    def has_open_position(self, symbol):

        return any(
            p.symbol == symbol and p.status == "OPEN"
            for p in self.positions
        )

    def close_position(
        self,
        position: PaperPosition,
        exit_price: float,
    ):

        commission = self.account.calculate_commission(
            position.quantity * exit_price
        )

        pnl = position.close(
            exit_price,
            commission
        )

        self.account.apply_trade_result(
            pnl,
            commission=0
        )

        self.closed_positions.append(position)

        return pnl

    def summary(self):

        return {

            "open_positions": len(

                [

                    p

                    for p in self.positions

                    if p.status == "OPEN"

                ]

            ),

            "closed_positions": len(

                self.closed_positions

            ),

            "account": self.account.summary()

        }
