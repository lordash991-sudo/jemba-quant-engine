from config.settings import *


class ConfigManager:

    @staticmethod
    def app_name():
        return APP_NAME

    @staticmethod
    def symbol():
        return DEFAULT_SYMBOL

    @staticmethod
    def interval():
        return DEFAULT_INTERVAL

    @staticmethod
    def database():
        return DATABASE_NAME

    @staticmethod
    def api_key():
        return BINGX_API_KEY

    @staticmethod
    def secret():
        return BINGX_SECRET