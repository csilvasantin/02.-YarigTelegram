import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Yarig.ai
YARIG_EMAIL = os.getenv("YARIG_EMAIL", "")
YARIG_PASSWORD = os.getenv("YARIG_PASSWORD", "")
