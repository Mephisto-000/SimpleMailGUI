"""應用程式主視窗：提供輸入欄位與寄信控制流程。"""

from __future__ import annotations

import threading
import customtkinter as ctk
from tkinter import messagebox

from app.mail_service import send_email
from app.log_service import log_info, log_exception
from .tab_container import TabContainer


class MainWindow(ctk.CTk):
    """包裝 CustomTkinter 視窗並處理寄信互動。"""

    def __init__(self):
        super().__init__()
        self.title("Simple Mail GUI")
        self.geometry("900x640")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 由 TabContainer 建立並管理所有頁籤
        self.tabs = TabContainer(self, self.send_email_thread)
        self.tabs.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # ------------------------------------------------------------------
    # 寄信處理
    # ------------------------------------------------------------------
    def send_email_thread(self):
        """以背景執行緒寄信，避免阻塞 UI。"""

        t = threading.Thread(target=self._send_email, daemon=True)
        t.start()

    def _send_email(self):
        """實際的寄信流程，確保 UI 更新透過 self.after 呼叫。"""

        self.after(0, self.tabs.disable_send_button)
        self.after(0, lambda: self.tabs.set_status("Sending..."))

        try:
            to_raw = self.tabs.get_recipients_raw()
            subject = self.tabs.get_subject()
            body = self.tabs.get_body()

            if not to_raw:
                warning_msg = "Please enter at least one recipient."
                self.after(0, lambda: messagebox.showwarning("Missing field", warning_msg))
                return

            # 支援逗號或分號分隔多個收件人
            to_addrs = [addr.strip() for addr in to_raw.replace(";", ",").split(",") if addr.strip()]
            attachments = self.tabs.get_attachments()

            log_info(f"📨 開始寄信給 {to_addrs}（附件 {len(attachments)} 個）...")
            send_email(to_addrs, subject, body, attachments=attachments)
            log_info("✅ 郵件寄出成功。")

            self.after(0, lambda: self.tabs.set_status("✅ Sent successfully."))
            self.after(0, lambda: messagebox.showinfo("Success", "Email sent successfully!"))

        except Exception as e:  # noqa: BLE001 - 保留一般例外記錄
            log_exception(e)
            self.after(0, lambda: self.tabs.set_status("❌ Failed to send."))
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to send email:\n{e}"))
        finally:
            self.after(0, self.tabs.enable_send_button)
