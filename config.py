import os

from dotenv import load_dotenv

load_dotenv()

TOKEN=os.getenv('TOKEN')
API_KEY=os.getenv('API_KEY')

DEFAULT_COMPANY=os.getenv('DEFAULT_COMPANY')
DEFAULT_PROJECT=os.getenv('DEFAULT_PROJECT')
DEFAULT_BOARD=os.getenv('DEFAULT_BOARD')
DEFAULT_COLUMN=os.getenv('DEFAULT_COLUMN')
SAVE_PATH=os.getenv('SAVE_PATH')
CUSTOM_LOCALE=os.getenv('CUSTOM_LOCALE')
ADMIN_TELEGRAM_IDS=os.getenv('ADMIN_TELEGRAM_IDS').split(',')