"""日誌服務：建立每日檔案並提供簡化的記錄函式。"""

import logging
import os
from datetime import datetime

# logs 目錄位於專案根目錄下，若不存在會自動建立
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 以日期分檔，方便追蹤每日寄信紀錄
LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now():%Y-%m-%d}.log")

# 建立同時輸出到檔案與終端機的記錄設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),  # 同時輸出到終端機
    ],
)

logger = logging.getLogger("SimpleMailGUI")


def log_info(message: str):
    """記錄一般資訊，例如寄信進度或成功訊息。"""
    logger.info(message)


def log_error(message: str):
    """記錄可預期的錯誤狀況，方便追蹤常見問題。"""
    logger.error(message)


def log_exception(exc: Exception):
    """在例外情況下輸出完整堆疊資訊，便於除錯。"""
    logger.exception(f"例外發生：{exc}")
