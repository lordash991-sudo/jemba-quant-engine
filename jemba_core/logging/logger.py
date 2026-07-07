from pathlib import Path

from loguru import logger

LOG_PATH = Path("logs")

LOG_PATH.mkdir(exist_ok=True)

logger.remove()

logger.add(
    LOG_PATH / "engine.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level="DEBUG",
    enqueue=True,
)

logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
)

logger.info("========================================")
logger.info("JEMBA QUANT ENGINE iniciado")
logger.info("========================================")