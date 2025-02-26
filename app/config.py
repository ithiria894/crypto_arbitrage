# app/config.py
import os
from dotenv import load_dotenv

# 讀取 .env 檔案中的環境變數
load_dotenv()

# 將環境變數讀取後存入變數，方便其他地方使用
# DATABASE_URL = os.getenv("DATABASE_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
