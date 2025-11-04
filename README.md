# SimpleMailGUI

A simple Python desktop mail sender built with CustomTkinter and SMTP.  
使用 CustomTkinter 製作的簡易郵件寄送桌面應用程式。

---

## Features 

- Modern CustomTkinter GUI with分頁式介面（寄信 / 附件 / 月曆）
- SMTP 郵件寄送（支援 STARTTLS / SSL、多收件者、附件）
- `.env` + `python-dotenv` 管理敏感設定
- APScheduler 排程：單次排程、每日排程、非假日每日排程
- 每日輪替的檔案日誌，記錄寄信結果與錯誤
- 模組化結構：應用層 (`app/`) 與 UI 層 (`ui/`) 清楚分離

---

## Project Structure

```bash=
SimpleMailGUI/
├── app/
│   ├── init.py          # Exports mail, config, and log modules
│   ├── config.py            # Load environment variables
│   ├── mail_service.py      # Core email sending logic
│   └── log_service.py       # Daily log writer
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # Main window + APScheduler interaction
│   ├── tab_container.py     # TabView 管理器
│   ├── tab_compose.py       # 寄信頁籤（含排程選項）
│   ├── tab_attachments.py   # 附件管理頁籤
│   └── tab_calendar.py      # 月曆頁籤（選擇單次排程時間）
│
├── logs/                    # Automatically generated daily logs
│   └── 2025-10-16.log
│
├── .env                     # Local configuration (not committed)
├── .env.example             # Example environment file
├── main.py                  # Application entry point
├── pyproject.toml
└── README.md
```

---

## Setup

### 1. Create Environment & Install Dependencies

```bash=
uv venv -p 3.13
uv sync
```

### 2. Create .env File

```bash=
cp .env.example .env
```

Then edit .env to include your SMTP configuration:
```bash=
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURITY=STARTTLS
SMTP_USER=your_email@example.com
SMTP_PASS=your_app_password
```

---

## Run Application 

```bash=
uv run python main.py
```

---

## Scheduling Options

排程開關位於「寄信」頁籤下方，一次只能啟用一種模式：

1. **開啟定時排程**：搭配「月曆」頁籤選擇日期與時間，點擊 Send 後會建立單次 APScheduler 工作。
2. **開啟每日排程**：勾選後選擇每日的 HH:MM，APS cheduler 會每天在該時間寄信。
3. **開啟非假日每日排程**：同樣選擇 HH:MM，僅在週一至週五觸發。

若沒有勾選排程，點擊 Send 會立即寄出郵件。切換到其他排程類型時，對應設定（例如月曆選擇）會自動重置，避免送出舊的排程。

---

## Build Executable with Nuitka

專案已加入 `nuitka` 套件，可將應用程式編譯成獨立可執行檔：

```bash=
uv run python -m nuitka \
  --follow-imports \
  --standalone \
  --onefile \
  --enable-plugin=tk-inter \
  --output-dir dist \
  main.py
```

- `--standalone --onefile` 會產出單一可攜執行檔（Windows 會放在 `dist/main.exe`）。
- `--enable-plugin=tk-inter` 必要，確保 CustomTkinter 所需的 Tk 元件正確打包。
- 若要內建 `.env` 或其他資源，可再使用 `--include-data-file` / `--include-data-dir` 參數。
