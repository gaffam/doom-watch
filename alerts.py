import logging
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram(msg: str) -> None:
    """Send a Telegram message using configured bot credentials."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.get(url, params={"text": msg, "chat_id": TELEGRAM_CHAT_ID}, timeout=10)
    except Exception as exc:
        logging.warning("telegram send failed: %s", exc)
