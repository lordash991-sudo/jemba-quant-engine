from unittest.mock import MagicMock, patch

from jemba_core.providers.bingx_provider import BingXProvider


def fake_response(payload):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


@patch("requests.get")
def test_ping(mock_get):
    mock_get.return_value = fake_response({})

    provider = BingXProvider()

    assert provider.ping()


@patch("requests.get")
def test_price(mock_get):
    mock_get.return_value = fake_response({"price": "100000"})

    provider = BingXProvider()

    data = provider.get_price("BTC-USDT")

    assert data["price"] == "100000"


@patch("requests.get")
def test_candles(mock_get):
    mock_get.return_value = fake_response([1, 2, 3])

    provider = BingXProvider()

    candles = provider.get_candles("BTC-USDT", "1h")

    assert len(candles) == 3


@patch("requests.get")
def test_latest(mock_get):
    mock_get.return_value = fake_response([{"close": 100}])

    provider = BingXProvider()

    candle = provider.get_latest("BTC-USDT", "1h")

    assert candle["close"] == 100


@patch("requests.get")
def test_latest_none(mock_get):
    mock_get.return_value = fake_response([])

    provider = BingXProvider()

    assert provider.get_latest("BTC-USDT", "1h") is None
