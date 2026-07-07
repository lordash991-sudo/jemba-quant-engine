import logging
import signal
import sys
import warnings

from jemba_core.engine.scheduler import Scheduler

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class QuantEngine:

    def __init__(self, mode="paper"):
        self.mode = mode
        self.scheduler = Scheduler()
        self.running = True

    def stop(self, *args):
        logging.info("Deteniendo motor...")
        self.running = False
        sys.exit(0)

    def start(self):
        logging.info("=" * 60)
        logging.info("JEMBA QUANT ENGINE")
        logging.info(f"MODO: {self.mode.upper()}")
        logging.info("=" * 60)

        if self.mode == "live":
            logging.warning("MODO LIVE ACTIVADO. Verificar API antes de operar.")
        else:
            logging.info("Modo PAPER activado. No se enviarán órdenes reales.")

        self.scheduler.run()


def main():
    mode = "paper"

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

    if mode not in ["paper", "live"]:
        raise ValueError("Modo inválido. Usa: paper o live")

    engine = QuantEngine(mode=mode)

    signal.signal(signal.SIGINT, engine.stop)
    signal.signal(signal.SIGTERM, engine.stop)

    engine.start()


if __name__ == "__main__":
    main()
