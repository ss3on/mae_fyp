import time
from scripts import telegram_update

notifier = telegram_update.TelegramNotifier(window_size=10)
for i in range(20):
    time.sleep(0.5)
    notifier.add_message(f'This is a test message {i}')