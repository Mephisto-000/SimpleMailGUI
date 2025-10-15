# SimpleMailGUI

A simple Python desktop mail sender built with CustomTkinter and SMTP.  
使用 CustomTkinter 製作的簡易郵件寄送桌面應用程式。

---

## Features 

- Send emails via SMTP (supports STARTTLS / SSL)
- Modern CustomTkinter GUI interface
- `.env` configuration for secure credentials
- Daily log file output for sent/failed records
- Modular architecture with clear separation between `app/` and `ui/`

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
│   ├── init.py          # Exports MainWindow
│   └── main_window.py       # CustomTkinter main GUI
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

### 1. Create Environment

```bash=
uv venv -p 3.13
uv sync
```

### 2. Install Dependencies

```bash=
uv add customtkinter python-dotenv
```

### 3. Create .env File

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
