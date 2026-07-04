from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = "JEMBA QUANT ENGINE"

DEBUG = True

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_SECRET = os.getenv("BINGX_SECRET")

DATABASE_NAME = "jemba.db"

DEFAULT_SYMBOL = "BTCUSDT"

DEFAULT_INTERVAL = "1h"

TIMEZONE = "UTC"