from time import sleep

from jemba_core.kernel.bootstrap import Bootstrap
from jemba_core.pipeline.pipeline_engine import PipelineEngine


class JembaKernel:
    def __init__(self, bootstrap=None):
        self.bootstrap = bootstrap or Bootstrap()
        self.container = None
        self.running = False
        self.market = None
        self.pipeline = None

    def start(self):
        if self.running:
            return self.container

        self.container = self.bootstrap.build()

        if self.pipeline is None:
            self.pipeline = PipelineEngine()

        self.running = True

        return self.container

    def stop(self):
        self.running = False
        self.container = None

    def run(self, cycles=1, delay=1):
        self.start()

        for _ in range(cycles):
            market_data = None

            if self.market is not None:
                market_data = self.market.update()

            if self.pipeline is not None:
                self.pipeline.execute(market_data)

            sleep(delay)

        return True

    @property
    def provider(self):
        if self.container is None:
            return None

        return self.container.provider

    @property
    def config(self):
        if self.container is None:
            return None

        return self.container.config
