"""應用程式主視窗：提供輸入欄位與寄信控制流程。"""

import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from app.mail_service import send_email
from app.log_service import log_info, log_exception


class MainWindow(ctk.CTk):
    """包裝 CustomTkinter 視窗並處理寄信互動。"""

    def __init__(self):
        super().__init__()
        self.title("Simple Mail GUI")
        self.geometry("900x640")

        # 追蹤附件檔案路徑
        self.attachments: list[str] = []

        # 主要版面切成頁籤：寄信 / 附件
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.compose_tab = self.tabview.add("寄信")
        self.attach_tab = self.tabview.add("附件")
        self.tabview.set("寄信")  # 初始畫面為寄信頁籤

        self._build_compose_tab()
        self._build_attachment_tab()

    # ------------------------------------------------------------------
    # 寄信頁籤 UI
    # ------------------------------------------------------------------
    def _build_compose_tab(self):
        """建立寄信頁籤的欄位與控制按鈕。"""

        self.compose_tab.grid_columnconfigure(1, weight=1)
        self.compose_tab.grid_rowconfigure(2, weight=1)

        # 收件人欄位
        ctk.CTkLabel(self.compose_tab, text="To:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.to_entry = ctk.CTkEntry(self.compose_tab, width=400, placeholder_text="someone@example.com")
        self.to_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # 主旨欄位
        ctk.CTkLabel(self.compose_tab, text="Subject:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.subject_entry = ctk.CTkEntry(self.compose_tab, width=400, placeholder_text="Subject")
        self.subject_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # 內文輸入
        ctk.CTkLabel(self.compose_tab, text="Body:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        self.body_text = ctk.CTkTextbox(self.compose_tab, width=600, height=320)
        self.body_text.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        # 附件摘要顯示
        self.attachment_summary = ctk.StringVar(value="附件：尚未選擇")
        ctk.CTkLabel(self.compose_tab, textvariable=self.attachment_summary).grid(
            row=3, column=1, padx=10, pady=(0, 5), sticky="w"
        )

        # 狀態列 + 寄信按鈕
        status_row = ctk.CTkFrame(self.compose_tab)
        status_row.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        status_row.grid_columnconfigure(0, weight=1)

        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(status_row, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky="w")

        self.send_btn = ctk.CTkButton(status_row, text="Send", command=self.send_email_thread)
        self.send_btn.grid(row=0, column=1, padx=(10, 0), sticky="e")

    # ------------------------------------------------------------------
    # 附件頁籤 UI
    # ------------------------------------------------------------------
    def _build_attachment_tab(self):
        """建立附件頁籤，提供檔案選取與列表。"""

        self.attach_tab.grid_columnconfigure(0, weight=1)
        self.attach_tab.grid_rowconfigure(1, weight=1)

        description = (
            "在此頁籤選擇附件檔案，將開啟系統檔案對話框。\n"
            "選取後會列在下方清單，寄信時會自動附上。"
        )
        ctk.CTkLabel(self.attach_tab, text=description, justify="left").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        btn_frame = ctk.CTkFrame(self.attach_tab)
        btn_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        ctk.CTkButton(btn_frame, text="選擇附件檔案", command=self.choose_attachments).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="清空附件", command=self.clear_attachments, fg_color="#a33c3c").grid(
            row=0, column=1, padx=5
        )

        # 使用不可編輯文字方塊列出附件
        self.attachment_box = ctk.CTkTextbox(self.attach_tab, width=760, height=360)
        self.attachment_box.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self._refresh_attachment_box()

    # ------------------------------------------------------------------
    # 附件操作
    # ------------------------------------------------------------------
    def choose_attachments(self):
        """開啟檔案對話框，允許多選附件。"""

        paths = filedialog.askopenfilenames(title="選擇附件檔案")
        if not paths:
            return

        for path in paths:
            if path not in self.attachments:
                self.attachments.append(path)

        self._refresh_attachment_box()
        self._update_attachment_summary()

    def clear_attachments(self):
        """清空附件清單。"""

        self.attachments.clear()
        self._refresh_attachment_box()
        self._update_attachment_summary()

    def _refresh_attachment_box(self):
        """依據附件清單更新顯示內容。"""

        self.attachment_box.configure(state="normal")
        self.attachment_box.delete("1.0", "end")
        if not self.attachments:
            self.attachment_box.insert("end", "尚未選擇任何附件。")
        else:
            for idx, path in enumerate(self.attachments, start=1):
                self.attachment_box.insert("end", f"{idx}. {path}\n")
        self.attachment_box.configure(state="disabled")

    def _update_attachment_summary(self):
        """更新寄信頁籤上的附件摘要文字。"""

        if not self.attachments:
            self.attachment_summary.set("附件：尚未選擇")
        else:
            self.attachment_summary.set(f"附件：{len(self.attachments)} 個檔案")

    # ------------------------------------------------------------------
    # 寄信處理
    # ------------------------------------------------------------------
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
            attachments = list(self.attachments)

            log_info(f"📨 開始寄信給 {to_addrs}（附件 {len(attachments)} 個）...")
            send_email(to_addrs, subject, body, attachments=attachments)
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
