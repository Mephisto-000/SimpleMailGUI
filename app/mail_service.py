import smtplib
from email.message import EmailMessage
from app import config
from app.log_service import log_info, log_error, log_exception

def send_email(to_addrs, subject, body, as_html=False):
    msg = EmailMessage()
    msg["From"] = config.SMTP_USER
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject

    if as_html:
        msg.set_content(body)
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    try:
        if config.SMTP_SECURITY == "SSL":
            smtp = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, timeout=30)
        else:
            smtp = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT, timeout=30)
            if config.SMTP_SECURITY == "STARTTLS":
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

        smtp.login(config.SMTP_USER, config.SMTP_PASS)
        smtp.send_message(msg)
        log_info(f"✅ 寄信成功 → 收件者: {to_addrs}, 主旨: {subject}")
    except smtplib.SMTPAuthenticationError:
        log_error("❌ 驗證失敗，請檢查帳密或應用程式密碼。")
        raise
    except Exception as e:
        log_exception(e)
        raise
    finally:
        try:
            smtp.quit()
        except Exception:
            pass
