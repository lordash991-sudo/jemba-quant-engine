from pathlib import Path

import yaml

from jemba_core.kernel.container import Container
from jemba_core.providers.bingx_provider import BingXProvider


class Bootstrap:

    def __init__(self, config_path="config/config.yaml"):
        self.config_path = Path(config_path)

    def build(self):
        container = Container()

        with open(self.config_path, "r", encoding="utf-8") as f:
            container.config = yaml.safe_load(f)

        broker = container.config.get("broker", "").lower()

        if broker == "bingx":
            container.provider = BingXProvider()
        else:
            raise ValueError(f"Broker no soportado: {broker}")

        return container
