"""
SMTP Mail Service
-----------------
提供完整的郵件寄送功能，包含：
- 支援 STARTTLS / SSL 加密連線
- 支援 To / Cc / Bcc 多收件者
- 支援純文字與 HTML 內容
- 支援附加檔案 (自動判斷 MIME 類型)
- 透過 app.config 載入 SMTP 設定
- 透過 app.log_service 記錄寄送結果與錯誤
"""

from __future__ import annotations

import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, List, Optional

from app import config
from app.log_service import log_info, log_error, log_exception


# ----------------------------------------------------------
# 工具函式：統一處理輸入型別
# ----------------------------------------------------------
def _ensure_list(x: Optional[Iterable[str]]) -> List[str]:
    """
    將傳入的收件者資訊轉成 List[str]
    若為 None 或空集合，回傳空清單。
    """
    if not x:
        return []
    return [s.strip() for s in x if s and s.strip()]


# ----------------------------------------------------------
# 工具函式：處理附件
# ----------------------------------------------------------
def _add_attachments(msg: EmailMessage, attachments: Iterable[str] | None) -> None:
    """
    附加檔案到郵件中，根據副檔名自動判斷 MIME 類型。
    若找不到檔案或無法判斷類型，會記錄錯誤但不會中斷寄信。
    """
    if not attachments:
        return
    for p in attachments:
        path = Path(p)
        if not path.is_file():
            log_error(f"附件不存在或不是檔案：{path}")
            continue

        # 嘗試判斷檔案類型，例如 "image/png" 或 "application/pdf"
        ctype, encoding = mimetypes.guess_type(path.name)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        # 以二進位方式讀取檔案內容
        with path.open("rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=path.name,
            )


# ----------------------------------------------------------
# 建立 EmailMessage 物件
# ----------------------------------------------------------
def build_message(
    sender: str,
    to_addrs: Iterable[str],
    subject: str,
    body: str,
    *,
    as_html: bool = False,
    cc: Iterable[str] | None = None,
    bcc: Iterable[str] | None = None,
    reply_to: Optional[str] = None,
    attachments: Iterable[str] | None = None,
) -> EmailMessage:
    """
    建立一封郵件物件，可支援 HTML、Cc、Bcc、回覆地址、附件等功能。
    """
    # 將收件人、抄送、密件抄送統一處理成清單
    to_list = _ensure_list(to_addrs)
    cc_list = _ensure_list(cc)
    bcc_list = _ensure_list(bcc)

    if not to_list and not cc_list and not bcc_list:
        raise ValueError("至少需要一個收件者（To / Cc / Bcc）")

    # 初始化郵件物件
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(to_list) if to_list else sender
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    if reply_to:
        msg["Reply-To"] = reply_to.strip()
    msg["Subject"] = subject

    # 根據 as_html 決定信件內容格式
    if as_html:
        # 為相容性保留純文字版本（部分郵件客戶端不支援 HTML）
        msg.set_content(body)  # 純文字
        msg.add_alternative(body, subtype="html")  # HTML
    else:
        msg.set_content(body)

    # 處理附件
    _add_attachments(msg, attachments)
    return msg


# ----------------------------------------------------------
# 建立 SMTP 連線
# ----------------------------------------------------------
def _connect_smtp() -> smtplib.SMTP:
    """
    根據設定建立 SMTP 或 SMTP_SSL 連線。
    STARTTLS 模式會自動執行加密升級。
    """
    if config.SMTP_SECURITY == "SSL":
        return smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, timeout=30)
    smtp = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT, timeout=30)
    if config.SMTP_SECURITY == "STARTTLS":
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
    return smtp


# ----------------------------------------------------------
# 寄送郵件主函式
# ----------------------------------------------------------
def send_email(
    to_addrs: Iterable[str],
    subject: str,
    body: str,
    *,
    as_html: bool = False,
    cc: Iterable[str] | None = None,
    bcc: Iterable[str] | None = None,
    reply_to: Optional[str] = None,
    attachments: Iterable[str] | None = None,
) -> str:
    """
    寄送郵件（使用 app/config 中的 SMTP 設定）。

    參數：
    --------
    to_addrs : 收件者清單
    subject  : 郵件主旨
    body     : 郵件內容（純文字或 HTML）
    as_html  : 是否以 HTML 模式寄出
    cc, bcc  : 抄送與密件抄送清單
    reply_to : 回覆地址（可選）
    attachments : 附件檔案路徑清單（可選）

    回傳：
    --------
    message_id : EmailMessage 所產生的 Message-ID（非伺服器端 ID）

    例外：
    --------
    若 SMTP 設定有誤或連線/驗證失敗，會拋出 smtplib 相關例外。
    """
    # 確認環境設定是否齊全
    if not (config.SMTP_SERVER and config.SMTP_PORT and config.SMTP_USER and config.SMTP_PASS):
        raise ValueError("SMTP 設定不完整，請確認 .env 或 app/config.py")

    # 建立郵件物件
    msg = build_message(
        sender=config.SMTP_USER,
        to_addrs=to_addrs,
        subject=subject,
        body=body,
        as_html=as_html,
        cc=cc,
        bcc=bcc,
        reply_to=reply_to,
        attachments=attachments,
    )

    # 組合所有收件人（實際寄送用）
    to_list = _ensure_list(to_addrs)
    cc_list = _ensure_list(cc)
    bcc_list = _ensure_list(bcc)
    all_recipients = to_list + cc_list + bcc_list or [config.SMTP_USER]

    smtp = None
    try:
        # 建立連線並登入
        smtp = _connect_smtp()
        smtp.login(config.SMTP_USER, config.SMTP_PASS)

        # 寄送郵件
        smtp.send_message(msg, to_addrs=all_recipients)
        mid = msg.get("Message-ID", "") or "<no-message-id>"

        log_info(
            f"寄信成功 → To:{to_list or ['(self)']} "
            f"Cc:{cc_list} Bcc:{len(bcc_list)} Subject:{subject} MID:{mid}"
        )
        return mid

    # 常見 SMTP 錯誤分類記錄
    except smtplib.SMTPAuthenticationError:
        log_error("驗證失敗：請檢查 SMTP_USER / SMTP_PASS 或應用程式密碼。")
        raise
    except smtplib.SMTPRecipientsRefused as e:
        log_error(f"收件人被拒絕：{e.recipients}")
        raise
    except smtplib.SMTPConnectError as e:
        log_error(f"無法連線至伺服器：{e}")
        raise
    except smtplib.SMTPServerDisconnected as e:
        log_error(f"伺服器連線中斷：{e}")
        raise
    except smtplib.SMTPSenderRefused as e:
        log_error(f"寄件人被拒絕：{e}")
        raise
    except Exception as e:
        # 捕捉所有其他未預期錯誤
        log_exception(e)
        raise
    finally:
        # 結束連線（安全關閉）
        if smtp is not None:
            try:
                smtp.quit()
            except Exception:
                pass
