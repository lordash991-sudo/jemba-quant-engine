class PaperAccount:

    def __init__(self, balance: float = 1000):
        self.balance = balance
        self.equity = balance
        self.open_position = None
        self.closed_positions = []

    def has_open_position(self):
        return self.open_position is not None

    def open(self, position):
        if self.has_open_position():
            raise RuntimeError("Ya existe una posicion abierta")

        self.open_position = position

    def close(self, exit_price: float):
        if not self.has_open_position():
            return None

        position = self.open_position

        if position.action == "BUY":
            pnl = (exit_price - position.entry) * position.quantity
        else:
            pnl = (position.entry - exit_price) * position.quantity

        position.pnl = round(pnl, 2)
        position.status = "CLOSED"

        self.balance = round(self.balance + position.pnl, 2)
        self.equity = self.balance

        self.closed_positions.append(position)
        self.open_position = None

        return position
