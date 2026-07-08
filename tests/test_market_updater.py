from unittest.mock import MagicMock

from jemba_core.engine.market_updater import MarketUpdater


def build_updater():
    provider = MagicMock()
    repository = MagicMock()
    event_bus = MagicMock()
    scheduler = MagicMock()

    provider.get_latest.return_value = {"close": 100}
    repository.save.return_value = True
    scheduler.should_continue.side_effect = [True, False]

    updater = MarketUpdater(
        market_provider=provider,
        candle_repository=repository,
        event_bus=event_bus,
        scheduler=scheduler,
        symbols=["BTC-USDT", "ETH-USDT"],
        timeframe="1h",
    )

    return updater, provider, repository, event_bus, scheduler


def test_update_symbol_downloads_candle():
    updater, provider, repository, event_bus, scheduler = build_updater()

    updater.update_symbol("BTC-USDT")

    provider.get_latest.assert_called_once()


def test_update_symbol_saves_candle():
    updater, provider, repository, event_bus, scheduler = build_updater()

    updater.update_symbol("BTC-USDT")

    repository.save.assert_called_once()


def test_update_symbol_publishes_event():
    updater, provider, repository, event_bus, scheduler = build_updater()

    updater.update_symbol("BTC-USDT")

    event_bus.publish.assert_called_once()


def test_update_symbol_returns_false_when_no_candle():
    updater, provider, repository, event_bus, scheduler = build_updater()
    provider.get_latest.return_value = None

    result = updater.update_symbol("BTC-USDT")

    assert result is False


def test_update_symbol_handles_provider_error():
    updater, provider, repository, event_bus, scheduler = build_updater()
    provider.get_latest.side_effect = Exception("provider error")

    result = updater.update_symbol("BTC-USDT")

    assert result is False


def test_update_all_processes_multiple_symbols():
    updater, provider, repository, event_bus, scheduler = build_updater()

    result = updater.update_all()

    assert result["BTC-USDT"] is True
    assert result["ETH-USDT"] is True
    assert provider.get_latest.call_count == 2


def test_run_once():
    updater, provider, repository, event_bus, scheduler = build_updater()

    result = updater.run_once()

    assert result["BTC-USDT"] is True


def test_run_calls_scheduler_sleep():
    updater, provider, repository, event_bus, scheduler = build_updater()

    updater.run()

    scheduler.sleep.assert_called_once()
