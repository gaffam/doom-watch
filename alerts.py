import requests


def send_telegram(msg: str) -> None:
    """Send a Telegram message using bot credentials."""
    bot_token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.get(url, params={"text": msg, "chat_id": chat_id}, timeout=10)
    except Exception:
        pass

