"""月曆頁籤：預留 APScheduler 排程功能的日期選擇介面。"""

from __future__ import annotations

import calendar
from datetime import date, datetime, time, timedelta

import customtkinter as ctk


class CalendarTab:
    """簡易月曆檢視，可切換月份並挑選排程日期時間。"""

    WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]

    def __init__(self, parent: ctk.CTkFrame):
        self.parent = parent
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)

        self.current_month = date.today().replace(day=1)
        self.selected_date: date | None = None
        self.scheduled_datetime: datetime | None = None

        self._build_header()
        self._build_calendar_grid()
        self._build_time_controls()
        self._render_calendar()

    # -- UI 結構 ----------------------------------------------------------
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self.parent)
        header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(header, text="◀ 上個月", width=100, command=self._goto_prev_month).grid(row=0, column=0, padx=5)

        self.month_label = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.month_label.grid(row=0, column=1, sticky="n")

        ctk.CTkButton(header, text="下個月 ▶", width=100, command=self._goto_next_month).grid(row=0, column=2, padx=5)

    def _build_calendar_grid(self) -> None:
        self.grid_frame = ctk.CTkFrame(self.parent)
        self.grid_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        for col in range(7):
            self.grid_frame.grid_columnconfigure(col, weight=1)

        # 星期標題列
        for col, name in enumerate(self.WEEKDAYS):
            lbl = ctk.CTkLabel(self.grid_frame, text=name, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

        # 預先建立 6 週的格子
        self.day_labels: list[ctk.CTkLabel] = []
        self.day_label_dates: list[date | None] = []
        for row in range(1, 7):
            for col in range(7):
                lbl = ctk.CTkLabel(self.grid_frame, text="", height=40, corner_radius=6)
                lbl.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
                index = len(self.day_labels)
                lbl.bind("<Button-1>", lambda _evt, idx=index: self._on_day_click(idx))
                self.day_labels.append(lbl)
                self.day_label_dates.append(None)

    def _build_time_controls(self) -> None:
        self.time_frame = ctk.CTkFrame(self.parent)
        self.time_frame.grid(row=2, column=0, padx=10, pady=(0, 15), sticky="ew")
        self.time_frame.grid_columnconfigure(1, weight=1)

        self.selection_label = ctk.CTkLabel(self.time_frame, text="尚未選擇排程時間")
        self.selection_label.grid(row=0, column=0, columnspan=4, sticky="w")

        ctk.CTkLabel(self.time_frame, text="排程時間：").grid(row=1, column=0, pady=(8, 0), sticky="w")

        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(60)]
        self.hour_var = ctk.StringVar(value=f"{datetime.now().hour:02d}")
        self.minute_var = ctk.StringVar(value=f"{(datetime.now().minute // 5) * 5:02d}")

        self.hour_menu = ctk.CTkOptionMenu(self.time_frame, values=hours, variable=self.hour_var, command=self._on_time_change)
        self.hour_menu.grid(row=1, column=1, padx=5, pady=(8, 0))

        self.minute_menu = ctk.CTkOptionMenu(self.time_frame, values=minutes, variable=self.minute_var, command=self._on_time_change)
        self.minute_menu.grid(row=1, column=2, padx=5, pady=(8, 0))

        ctk.CTkLabel(self.time_frame, text="(24 小時制，先點擊日期再選擇時間)").grid(row=1, column=3, padx=(5, 0), pady=(8, 0), sticky="w")
        self._update_selection_label()

    # -- 互動 -------------------------------------------------------------
    def _goto_prev_month(self) -> None:
        self.current_month = (self.current_month - timedelta(days=1)).replace(day=1)
        self.selected_date = None
        self._render_calendar()
        self._update_selection_label()

    def _goto_next_month(self) -> None:
        days_in_month = calendar.monthrange(self.current_month.year, self.current_month.month)[1]
        self.current_month = (self.current_month + timedelta(days=days_in_month)).replace(day=1)
        self.selected_date = None
        self._render_calendar()
        self._update_selection_label()

    def _on_day_click(self, index: int) -> None:
        day_date = self.day_label_dates[index]
        if not day_date:
            return
        self.selected_date = day_date
        self._render_calendar()
        self._update_selection_label()

    def _on_time_change(self, _value: str) -> None:
        self._update_selection_label()

    # -- 渲染 -------------------------------------------------------------
    def _render_calendar(self) -> None:
        year, month = self.current_month.year, self.current_month.month
        self.month_label.configure(text=f"{year} 年 {month:02d} 月")

        month_matrix = calendar.monthcalendar(year, month)
        today = date.today()

        for idx, lbl in enumerate(self.day_labels):
            lbl.configure(text="", fg_color="transparent")
            self.day_label_dates[idx] = None

        for row_idx, week in enumerate(month_matrix):
            for col_idx, day in enumerate(week):
                label_idx = row_idx * 7 + col_idx
                if day == 0:
                    self.day_labels[label_idx].configure(text="", text_color="gray50")
                    continue

                day_date = date(year, month, day)
                self.day_label_dates[label_idx] = day_date

                is_today = day_date == today
                is_selected = self.selected_date == day_date

                if is_selected:
                    fg_color = "#fbbf24"
                    text_color = "black"
                elif is_today:
                    fg_color = "#1f6aa5"
                    text_color = "white"
                else:
                    fg_color = "transparent"
                    text_color = "gray50" if col_idx in (5, 6) else "white"

                self.day_labels[label_idx].configure(
                    text=f"{day:2d}",
                    fg_color=fg_color,
                    text_color=text_color,
                )

    # -- 對外 API --------------------------------------------------------
    def get_scheduled_datetime(self) -> datetime | None:
        return self.scheduled_datetime

    # -- 內部 -------------------------------------------------------------
    def _update_selection_label(self) -> None:
        if not self.selected_date:
            self.scheduled_datetime = None
            self.selection_label.configure(text="尚未選擇排程時間")
            return

        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        self.scheduled_datetime = datetime.combine(self.selected_date, time(hour=hour, minute=minute))
        self.selection_label.configure(
            text=f"已選擇排程：{self.scheduled_datetime.strftime('%Y-%m-%d %H:%M')}"
        )
