import os
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    DEBUG = os.getenv('DEBUG')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    TG_BASE_URL = os.getenv('TG_BASE_URL')
    OPEN_EXCHANGE_RATES_API_KEY = os.getenv('OPEN_EXCHANGE_RATES_API_KEY')
    HOLIDAY_API_KEY = os.getenv('HOLIDAY_API_KEY')
