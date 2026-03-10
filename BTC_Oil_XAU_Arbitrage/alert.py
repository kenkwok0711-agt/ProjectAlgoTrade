# alert.py
# Module to send Telegram alerts.

import requests

def send_telegram_alert(token, chat_id, message):
    """
    Send message to Telegram chat.
    Requires internet access.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Telegram alert sent successfully.")
        else:
            print(f"Failed to send Telegram alert: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")