import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
BASE_URL = os.getenv('BASE_URL')
CARD_NUMBER = os.getenv('CARD_NUMBER')
MONTHLY_PAYMENT = int(os.getenv('MONTHLY_PAYMENT', 20000))
ADMIN_ID = [5953769207]