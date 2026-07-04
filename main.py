from jemba_core.logging.logger import logger
from jemba_core.utils.config_manager import ConfigManager

logger.info(f"Proyecto : {ConfigManager.app_name()}")
logger.info(f"Activo   : {ConfigManager.symbol()}")
logger.info(f"Intervalo: {ConfigManager.interval()}")
logger.info(f"Base DB  : {ConfigManager.database()}")