import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from jemba_core.paper.paper_account import PaperAccount
from jemba_core.paper.paper_broker import PaperBroker
from jemba_core.signals.signal_engine import TradeSignal

account = PaperAccount(balance=1000)
broker = PaperBroker(account)

signal = TradeSignal(
    symbol="BTC-USDT",
    timeframe="1h",
    action="BUY",
    entry=62500,
    quantity=0.01,
    stop_loss=61500,
    take_profit=64500,
    risk_amount=10,
)

position = broker.execute(signal)

print("POSICION ABIERTA:")
print(position)

candle = {"high": 64600, "low": 62400}

closed = broker.update(candle)

print()
print("POSICION CERRADA:")
print(closed)

print()
print("BALANCE:")
print(account.balance)
