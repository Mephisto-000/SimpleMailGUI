"""應用程式主視窗：提供輸入欄位與寄信控制流程。"""

import threading
import customtkinter as ctk
from tkinter import messagebox

from app.mail_service import send_email
from app.log_service import log_info, log_exception


class MainWindow(ctk.CTk):
    """包裝 CustomTkinter 視窗並處理寄信互動。"""

    def __init__(self):
        super().__init__()
        self.title("Simple Mail GUI")
        self.geometry("800x600")

        # 調整網格配置，讓輸入框能隨視窗縮放
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # 收件人欄位
        ctk.CTkLabel(self, text="To:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.to_entry = ctk.CTkEntry(self, width=400, placeholder_text="someone@example.com")
        self.to_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # 主旨欄位
        ctk.CTkLabel(self, text="Subject:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.subject_entry = ctk.CTkEntry(self, width=400, placeholder_text="Subject")
        self.subject_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # 內文輸入
        ctk.CTkLabel(self, text="Body:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        self.body_text = ctk.CTkTextbox(self, width=600, height=300)
        self.body_text.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        # 狀態列顯示寄送結果
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(self, textvariable=self.status_var)
        self.status_label.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # 寄信按鈕
        self.send_btn = ctk.CTkButton(self, text="Send", command=self.send_email_thread)
        self.send_btn.grid(row=5, column=1, padx=10, pady=20, sticky="e")

    def send_email_thread(self):
        """以背景執行緒寄信，避免阻塞 UI。"""

        t = threading.Thread(target=self._send_email, daemon=True)
        t.start()

    def _send_email(self):
        """實際的寄信流程，確保 UI 更新透過 self.after 呼叫。"""

        # UI 操作需排回主執行緒
        self.after(0, lambda: self.send_btn.configure(state="disabled"))
        self.after(0, lambda: self.status_var.set("Sending..."))

        try:
            to_raw = self.to_entry.get().strip()
            subject = self.subject_entry.get().strip()
            body = self.body_text.get("1.0", "end").strip()

            if not to_raw:
                warning_msg = "Please enter at least one recipient."
                self.after(0, lambda: messagebox.showwarning("Missing field", warning_msg))
                return

            # 支援逗號或分號分隔多個收件人
            to_addrs = [addr.strip() for addr in to_raw.replace(";", ",").split(",") if addr.strip()]
            log_info(f"📨 開始寄信給 {to_addrs}...")
            send_email(to_addrs, subject, body)
            log_info("✅ 郵件寄出成功。")

            # 使用 after 確保訊息盒呼叫在主緒上執行
            self.after(0, lambda: self.status_var.set("✅ Sent successfully."))
            self.after(0, lambda: messagebox.showinfo("Success", "Email sent successfully!"))

        except Exception as e:  # noqa: BLE001 - 保留一般例外記錄
            log_exception(e)
            self.after(0, lambda: self.status_var.set("❌ Failed to send."))
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to send email:\n{e}"))
        finally:
            self.after(0, lambda: self.send_btn.configure(state="normal"))
