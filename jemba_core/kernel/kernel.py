from jemba_core.kernel.bootstrap import Bootstrap


class JembaKernel:

    def __init__(self, bootstrap=None):
        self.bootstrap = bootstrap or Bootstrap()
        self.container = None
        self.running = False

    def start(self):
        if self.running:
            return self.container

        self.container = self.bootstrap.build()
        self.running = True

        return self.container

    def stop(self):
        self.running = False
        self.container = None

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
