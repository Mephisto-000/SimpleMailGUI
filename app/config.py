"""集中管理 SMTP 與環境設定，啟動時即讀取 .env 內容。"""

import os
from dotenv import load_dotenv

# 載入專案根目錄下的 .env 變數
load_dotenv()

# 郵件伺服器位址，預設為 Gmail SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
# 連線埠號，預設 587（STARTTLS 常用埠）
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
# 加密模式：允許 STARTTLS 或 SSL，統一轉為大寫方便比較
SMTP_SECURITY = os.getenv("SMTP_SECURITY", "STARTTLS").upper()
# 寄件者帳號（需與 SMTP 驗證相同）
SMTP_USER = os.getenv("SMTP_USER")
# 寄件者密碼或應用程式密碼
SMTP_PASS = os.getenv("SMTP_PASS")
