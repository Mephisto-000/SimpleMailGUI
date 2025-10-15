# app/__init__.py
"""
App package — 負責應用邏輯，包括：
- 設定載入 (config)
- 郵件寄送 (mail_service)
- 日誌記錄 (log_service)
"""

from .config import *
from .mail_service import send_email
from .log_service import log_info, log_error, log_exception

__all__ = [
    "send_email",
    "log_info",
    "log_error",
    "log_exception",
]

