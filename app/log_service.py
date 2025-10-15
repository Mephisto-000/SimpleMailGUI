import logging
import os
from datetime import datetime

# logs 目錄
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 每日一檔，例如 logs/2025-10-16.log
LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now():%Y-%m-%d}.log")

# 基本設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()  # 同時輸出到終端機
    ]
)

logger = logging.getLogger("SimpleMailGUI")

def log_info(message: str):
    logger.info(message)

def log_error(message: str):
    logger.error(message)

def log_exception(exc: Exception):
    logger.exception(f"例外發生：{exc}")
