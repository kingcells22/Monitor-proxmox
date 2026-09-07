import requests
import logging

TELEGRAM_BOT_TOKEN = "7930279041:AAG3eTyWwxJg6Zwj5euX0VR8cepB9P3ug9A"
TELEGRAM_CHAT_ID = "1292808439"  # Reemplaza por tu chat ID numérico

def send_telegram_alert(message: str):
    """
    Envía un mensaje de alerta por Telegram usando el bot configurado.
    Incluye logs detallados para debug.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        logging.info(f"Telegram response status: {response.status_code}")
        logging.info(f"Telegram response text: {response.text}")
        response.raise_for_status()
        if not response.json().get("ok"):
            logging.error(f"Telegram API error: {response.json()}")
    except Exception as e:
        logging.error(f"Error enviando alerta por Telegram: {e}")
