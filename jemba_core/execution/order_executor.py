from dataclasses import dataclass


@dataclass
class OrderResult:
    success: bool
    message: str
    order_id: str = ""


class OrderExecutor:

    def __init__(self, provider):
        self.provider = provider

    def execute(self, signal):
        if signal is None:
            return OrderResult(False, "No hay señal")

        side = "BUY" if signal.action == "BUY" else "SELL"

        try:
            result = self.provider.place_market_order(
                symbol=signal.symbol,
                side=side,
                quantity=signal.quantity,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit
            )

            return OrderResult(
                True,
                "Orden enviada",
                str(result.get("orderId", ""))
            )

        except Exception as e:
            return OrderResult(False, str(e))
