"""頁籤容器：統一管理寄信與附件頁籤。"""

from __future__ import annotations

import customtkinter as ctk

from .tab_compose import ComposeTab
from .tab_attachments import AttachmentTab
from .tab_calendar import CalendarTab


class TabContainer:
    """建立 TabView 並整合各個頁籤的對外介面。"""

    def __init__(self, master: ctk.CTkFrame, on_send):
        self.tabview = ctk.CTkTabview(master)
        compose_frame = self.tabview.add("寄信")
        attachment_frame = self.tabview.add("附件")
        calendar_frame = self.tabview.add("月曆")
        self.tabview.set("寄信")

        self.compose_tab = ComposeTab(compose_frame, on_send)
        self.attachment_tab = AttachmentTab(attachment_frame, self._handle_attachment_change)
        self.calendar_tab = CalendarTab(calendar_frame)

    # -- 佈局 -------------------------------------------------------------
    def grid(self, *args, **kwargs):
        self.tabview.grid(*args, **kwargs)

    # -- 對外 API --------------------------------------------------------
    def get_recipients_raw(self) -> str:
        return self.compose_tab.get_recipients_raw()

    def get_subject(self) -> str:
        return self.compose_tab.get_subject()

    def get_body(self) -> str:
        return self.compose_tab.get_body()

    def get_attachments(self) -> list[str]:
        return self.attachment_tab.get_attachments()

    def get_schedule_options(self) -> dict:
        return self.compose_tab.get_schedule_options()

    def get_calendar_datetime(self):
        return self.calendar_tab.get_scheduled_datetime()

    def set_status(self, text: str) -> None:
        self.compose_tab.set_status(text)

    def disable_send_button(self) -> None:
        self.compose_tab.disable_send_button()

    def enable_send_button(self) -> None:
        self.compose_tab.enable_send_button()

    # -- 內部 -------------------------------------------------------------
    def _handle_attachment_change(self, count: int) -> None:
        self.compose_tab.update_attachment_summary(count)
