"""附件頁籤：提供檔案選取與清單顯示功能。"""

from __future__ import annotations

import customtkinter as ctk
from tkinter import filedialog


class AttachmentTab:
    """封裝附件操作並在異動時回呼通知。"""

    def __init__(self, parent: ctk.CTkFrame, on_change):
        self.parent = parent
        self.on_change = on_change
        self.attachments: list[str] = []

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        description = (
            "在此頁籤選擇附件檔案，將開啟系統檔案對話框。\n"
            "選取後會列在下方清單，寄信時會自動附上。"
        )
        ctk.CTkLabel(parent, text=description, justify="left").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        btn_frame = ctk.CTkFrame(parent)
        btn_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        ctk.CTkButton(btn_frame, text="選擇附件檔案", command=self.choose_attachments).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="清空附件", command=self.clear_attachments, fg_color="#a33c3c").grid(
            row=0, column=1, padx=5
        )

        self.attachment_box = ctk.CTkTextbox(parent, width=760, height=360)
        self.attachment_box.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self._refresh_attachment_box()

    # -- 外部 API ---------------------------------------------------------
    def get_attachments(self) -> list[str]:
        return list(self.attachments)

    # -- 內部行為 ---------------------------------------------------------
    def choose_attachments(self) -> None:
        paths = filedialog.askopenfilenames(title="選擇附件檔案")
        if not paths:
            return
        for path in paths:
            if path not in self.attachments:
                self.attachments.append(path)

        self._refresh_attachment_box()
        self._notify_change()

    def clear_attachments(self) -> None:
        if not self.attachments:
            return
        self.attachments.clear()
        self._refresh_attachment_box()
        self._notify_change()

    def _refresh_attachment_box(self) -> None:
        self.attachment_box.configure(state="normal")
        self.attachment_box.delete("1.0", "end")
        if not self.attachments:
            self.attachment_box.insert("end", "尚未選擇任何附件。")
        else:
            for idx, path in enumerate(self.attachments, start=1):
                self.attachment_box.insert("end", f"{idx}. {path}\n")
        self.attachment_box.configure(state="disabled")

    def _notify_change(self) -> None:
        if self.on_change:
            self.on_change(len(self.attachments))
