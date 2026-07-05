import logging
import signal
import sys

from jemba_core.engine.scheduler import Scheduler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class QuantEngine:

    def __init__(self):

        self.scheduler = Scheduler()

        self.running = True

    def stop(self, *args):

        logging.info("Deteniendo motor...")

        self.running = False

        sys.exit(0)

    def start(self):

        logging.info("=" * 60)

        logging.info("JEMBA QUANT ENGINE")

        logging.info("=" * 60)

        self.scheduler.run()


def main():

    engine = QuantEngine()

    signal.signal(signal.SIGINT, engine.stop)

    signal.signal(signal.SIGTERM, engine.stop)

    engine.start()


if __name__ == "__main__":

    main()