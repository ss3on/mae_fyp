import os
import requests
import tkinter as tk
from tkinter import simpledialog
from collections import deque
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self, window_size=10, auto_flush=True, log_enabled=True):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not self.bot_token or not self.chat_id:
            raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env")
        self.window_size = window_size
        self.auto_flush = auto_flush
        self.log_enabled = log_enabled
        self.context_window = deque()

    def add_message(self, msg):
        """Add a message and auto-send if window is full."""
        self.context_window.append(msg)
        if self.auto_flush and len(self.context_window) >= self.window_size:
            self.send_update()

    def send_update(self, prefix="📢 Update"):
        """Send a batched update with context window messages."""
        if not self.context_window:
            print("⚠️ No messages to send.")
            return

        combined = "\n".join(f"- {m}" for m in self.context_window)
        full_message = f"{prefix}:\n{combined}"

        if len(full_message) <= 4096:
            self._send_text(full_message)
        else:
            self._send_markdown_file(full_message)

        self.context_window.clear()

    def _send_text(self, message):
        """Send a plain text message."""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(url, json=payload)
            if response.ok:
                print("✅ Telegram text message sent.")
            else:
                print(f"❌ Telegram text failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"⚠️ Exception during Telegram text send: {e}")

    def _send_markdown_file(self, content, filename="update.md"):
        """Send content as a Markdown file if too long."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            with open(filename, "rb") as f:
                files = {"document": f}
                data = {
                    "chat_id": self.chat_id,
                    "caption": "📄 Message too long—sent as Markdown file."
                }
                url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
                response = requests.post(url, files=files, data=data)
                if response.ok:
                    print("✅ Telegram Markdown file sent.")
                else:
                    print(f"❌ Telegram file failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"⚠️ Exception during Telegram file send: {e}")
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def log(self, message):
        """Optional audit logging."""
        if self.log_enabled:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")
