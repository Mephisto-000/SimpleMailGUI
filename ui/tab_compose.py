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

        # 排程設定
        self.schedule_frame = ctk.CTkFrame(parent)
        self.schedule_frame.grid(row=5, column=1, padx=10, pady=(5, 10), sticky="ew")
        self.schedule_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.schedule_frame, text="排程設定", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )

        self.schedule_once_var = ctk.BooleanVar(value=False)
        self.daily_var = ctk.BooleanVar(value=False)
        self.weekday_var = ctk.BooleanVar(value=False)

        self.schedule_once_chk = ctk.CTkCheckBox(
            self.schedule_frame,
            text="1. 開啟定時排程",
            variable=self.schedule_once_var,
            command=self._on_schedule_toggle,
        )
        self.schedule_once_chk.grid(row=1, column=0, columnspan=3, sticky="w")

        self.daily_chk = ctk.CTkCheckBox(
            self.schedule_frame,
            text="2. 開啟每日排程",
            variable=self.daily_var,
            command=self._on_schedule_toggle,
        )
        self.daily_chk.grid(row=2, column=0, columnspan=3, sticky="w")

        self.weekday_chk = ctk.CTkCheckBox(
            self.schedule_frame,
            text="3. 開啟非假日每日排程",
            variable=self.weekday_var,
            command=self._on_schedule_toggle,
        )
        self.weekday_chk.grid(row=3, column=0, columnspan=3, sticky="w")

        # 每日排程時間選擇 (當勾選 2 或 3 時顯示)
        self.daily_time_frame = ctk.CTkFrame(self.schedule_frame)
        self.daily_time_frame.grid(row=4, column=0, columnspan=3, pady=(5, 0), sticky="w")
        ctk.CTkLabel(self.daily_time_frame, text="每日寄送時間：").grid(row=0, column=0, padx=(0, 10))

        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        self.daily_hour_var = ctk.StringVar(value="09")
        self.daily_min_var = ctk.StringVar(value="00")

        self.daily_hour_menu = ctk.CTkOptionMenu(
            self.daily_time_frame, values=hours, variable=self.daily_hour_var, command=lambda _v: None
        )
        self.daily_hour_menu.grid(row=0, column=1, padx=5)

        self.daily_min_menu = ctk.CTkOptionMenu(
            self.daily_time_frame, values=minutes, variable=self.daily_min_var, command=lambda _v: None
        )
        self.daily_min_menu.grid(row=0, column=2, padx=5)

        ctk.CTkLabel(self.daily_time_frame, text="(24 小時制)").grid(row=0, column=3, padx=(5, 0))

        self.daily_time_frame.grid_remove()

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

    def get_schedule_options(self) -> dict:
        """回傳排程相關設定供主視窗使用。"""

        return {
            "use_calendar": self.schedule_once_var.get(),
            "daily": self.daily_var.get(),
            "weekday": self.weekday_var.get(),
            "daily_time": (int(self.daily_hour_var.get()), int(self.daily_min_var.get())),
        }

    # -- 內部 -------------------------------------------------------------
    def _on_schedule_toggle(self) -> None:
        """顯示或隱藏每日排程時間選單。"""

        if self.daily_var.get() or self.weekday_var.get():
            self.daily_time_frame.grid()
        else:
            self.daily_time_frame.grid_remove()
