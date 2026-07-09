from __future__ import annotations

import pytest

from jemba_core.ai.trainer.registry import ModelRegistry


def test_register():

    registry = ModelRegistry()

    class Dummy:
        pass

    registry.register("dummy", Dummy)

    assert registry.get("dummy") is Dummy


def test_unknown():

    registry = ModelRegistry()

    with pytest.raises(KeyError):
        registry.get("missing")
