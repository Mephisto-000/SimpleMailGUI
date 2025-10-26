"""寄信頁籤：負責基本郵件欄位與狀態列。"""

from __future__ import annotations

import customtkinter as ctk


class ComposeTab:
    """封裝寄信頁籤元素，提供資料讀取與狀態控制。"""

    def __init__(self, parent: ctk.CTkFrame, on_send):
        self.parent = parent
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        # 收件人欄位
        ctk.CTkLabel(parent, text="To:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.to_entry = ctk.CTkEntry(parent, width=400, placeholder_text="someone@example.com")
        self.to_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # 主旨欄位
        ctk.CTkLabel(parent, text="Subject:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.subject_entry = ctk.CTkEntry(parent, width=400, placeholder_text="Subject")
        self.subject_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # 信件內容
        ctk.CTkLabel(parent, text="Body:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        self.body_text = ctk.CTkTextbox(parent, width=600, height=320)
        self.body_text.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        # 附件摘要
        self.attachment_summary = ctk.StringVar(value="附件：尚未選擇")
        ctk.CTkLabel(parent, textvariable=self.attachment_summary).grid(
            row=3, column=1, padx=10, pady=(0, 5), sticky="w"
        )

        # 狀態列 + 寄信按鈕
        status_row = ctk.CTkFrame(parent)
        status_row.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        status_row.grid_columnconfigure(0, weight=1)

        self.status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(status_row, textvariable=self.status_var).grid(row=0, column=0, sticky="w")

        self.send_btn = ctk.CTkButton(status_row, text="Send", command=on_send)
        self.send_btn.grid(row=0, column=1, padx=(10, 0), sticky="e")

    # -- 資料存取 ---------------------------------------------------------
    def get_recipients_raw(self) -> str:
        return self.to_entry.get().strip()

    def get_subject(self) -> str:
        return self.subject_entry.get().strip()

    def get_body(self) -> str:
        return self.body_text.get("1.0", "end").strip()

    # -- 狀態控制 ---------------------------------------------------------
    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def disable_send_button(self) -> None:
        self.send_btn.configure(state="disabled")

    def enable_send_button(self) -> None:
        self.send_btn.configure(state="normal")

    def update_attachment_summary(self, count: int) -> None:
        if count <= 0:
            self.attachment_summary.set("附件：尚未選擇")
        else:
            self.attachment_summary.set(f"附件：{count} 個檔案")
