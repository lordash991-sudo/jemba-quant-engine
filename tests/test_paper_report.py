import json

from jemba_core.paper.paper_report import PaperReport


def test_save_summary(tmp_path):
    report = PaperReport(output_dir=tmp_path)

    path = report.save_summary(
        {
            "balance": 10100,
            "trades": 2,
        }
    )

    assert path.exists()

    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["balance"] == 10100
    assert data["trades"] == 2


def test_save_trades(tmp_path):
    report = PaperReport(output_dir=tmp_path)

    path = report.save_trades(
        [
            {
                "symbol": "BTC-USDT",
                "side": "BUY",
                "pnl": 100,
            }
        ]
    )

    assert path.exists()

    text = path.read_text(encoding="utf-8")

    assert "BTC-USDT" in text
    assert "BUY" in text
