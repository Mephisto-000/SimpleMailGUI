"""應用程式主視窗：提供輸入欄位與寄信控制流程。"""

from __future__ import annotations

import threading
from datetime import datetime
from uuid import uuid4

import customtkinter as ctk
from tkinter import messagebox

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.mail_service import send_email
from app.log_service import log_info, log_exception
from .tab_container import TabContainer


class MainWindow(ctk.CTk):
    """包裝 CustomTkinter 視窗並處理寄信互動。"""

    def __init__(self):
        super().__init__()
        self.title("Simple Mail GUI")
        self.geometry("900x640")

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

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
            schedule_opts = self.tabs.get_schedule_options()
            calendar_dt = self.tabs.get_calendar_datetime()

            if not to_raw:
                warning_msg = "Please enter at least one recipient."
                self.after(0, lambda: messagebox.showwarning("Missing field", warning_msg))
                return

            # 支援逗號或分號分隔多個收件人
            to_addrs = [addr.strip() for addr in to_raw.replace(";", ",").split(",") if addr.strip()]
            attachments = list(self.tabs.get_attachments())

            schedule_enabled = (
                schedule_opts["use_calendar"]
                or schedule_opts["daily"]
                or schedule_opts["weekday"]
            )

            if schedule_opts["use_calendar"] and calendar_dt is None:
                msg = "請先在「月曆」頁籤點選日期並設定時間。"
                self.after(0, lambda: messagebox.showwarning("排程設定不完整", msg))
                return

            payload = {
                "to_addrs": to_addrs,
                "subject": subject,
                "body": body,
                "attachments": attachments,
            }

            if schedule_enabled:
                try:
                    descriptions = self._schedule_jobs(payload, schedule_opts, calendar_dt)
                except ValueError as exc:
                    self.after(0, lambda: self.tabs.set_status("❌ Schedule failed."))
                    self.after(0, lambda: messagebox.showwarning("排程設定錯誤", str(exc)))
                else:
                    summary = "\n".join(f"• {desc}" for desc in descriptions)
                    log_info("📅 已建立排程：" + " / ".join(descriptions))
                    self.after(0, lambda: self.tabs.set_status("📅 Scheduled"))
                    self.after(
                        0,
                        lambda: messagebox.showinfo(
                            "已建立排程",
                            f"以下排程已透過 APScheduler 建立：\n{summary}",
                        ),
                    )
                return

            self._send_immediate(payload)

        except Exception as e:  # noqa: BLE001 - 保留一般例外記錄
            log_exception(e)
            self.after(0, lambda: self.tabs.set_status("❌ Failed to send."))
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to send email:\n{e}"))
        finally:
            self.after(0, self.tabs.enable_send_button)

    def _send_immediate(self, payload: dict) -> None:
        """立即寄送郵件，供非排程狀態使用。"""

        to_addrs = payload["to_addrs"]
        subject = payload["subject"]
        body = payload["body"]
        attachments = payload["attachments"]

        log_info(f"📨 開始寄信給 {to_addrs}（附件 {len(attachments)} 個）...")
        send_email(to_addrs, subject, body, attachments=attachments)
        log_info("✅ 郵件寄出成功。")

        self.after(0, lambda: self.tabs.set_status("✅ Sent successfully."))
        self.after(0, lambda: messagebox.showinfo("Success", "Email sent successfully!"))

    def _schedule_jobs(self, payload: dict, schedule_opts: dict, calendar_dt) -> list[str]:
        """依照排程設定建立 APScheduler 任務，回傳描述清單。"""

        descriptions: list[str] = []
        hour, minute = schedule_opts["daily_time"]
        now = datetime.now()

        if schedule_opts["use_calendar"]:
            if calendar_dt is None:
                raise ValueError("請在月曆頁籤選擇日期與時間。")
            if calendar_dt <= now:
                raise ValueError("排程時間必須晚於目前時間。")
            desc = f"單次排程：{calendar_dt:%Y-%m-%d %H:%M}"
            self.scheduler.add_job(
                self._run_scheduled_send,
                trigger="date",
                run_date=calendar_dt,
                args=[payload, desc],
                id=f"once-{uuid4()}",
                replace_existing=False,
            )
            descriptions.append(desc)

        if schedule_opts["daily"]:
            desc = f"每日 {hour:02d}:{minute:02d}"
            trigger = CronTrigger(hour=hour, minute=minute)
            self.scheduler.add_job(
                self._run_scheduled_send,
                trigger=trigger,
                args=[payload, desc],
                id=f"daily-{uuid4()}",
                replace_existing=False,
            )
            descriptions.append(desc)

        if schedule_opts["weekday"]:
            desc = f"週一至週五 {hour:02d}:{minute:02d}"
            trigger = CronTrigger(day_of_week="mon-fri", hour=hour, minute=minute)
            self.scheduler.add_job(
                self._run_scheduled_send,
                trigger=trigger,
                args=[payload, desc],
                id=f"weekday-{uuid4()}",
                replace_existing=False,
            )
            descriptions.append(desc)

        if not descriptions:
            raise ValueError("請至少選擇一種排程方式。")

        return descriptions

    def _run_scheduled_send(self, payload: dict, job_desc: str) -> None:
        """供 APScheduler 呼叫的背景寄信任務。"""

        try:
            log_info(f"📅 [排程觸發] {job_desc} → 目的地 {payload['to_addrs']}")
            send_email(payload["to_addrs"], payload["subject"], payload["body"], attachments=payload["attachments"])
            log_info(f"✅ [排程完成] {job_desc}")
        except Exception as exc:  # noqa: BLE001
            log_exception(exc)

    def _on_close(self):
        """視窗關閉時停止排程器並釋放資源。"""

        try:
            self.scheduler.shutdown(wait=False)
        except Exception:
            pass
        self.destroy()
