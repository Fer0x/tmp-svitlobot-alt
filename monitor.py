import socket
import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
TARGET_ADDRESS = os.getenv('TARGET_ADDRESS')

STATE_FILE = "state.txt"

def send_tg_message(text):
    if not BOT_TOKEN or not CHANNEL_ID:
        print(f"[LOCAL TEST] Telegram Message: {text}")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHANNEL_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"Error sending TG message: {e}")

def check_status():
    ip, port = TARGET_ADDRESS.split(':')
    port = int(port)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(7)
        try:
            s.connect((ip, port))
            return "online"
        except:
            return "offline"


if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        line = f.read().strip()
        if "|" in line:
            prev_state, prev_time_str = line.split("|")
            prev_time = datetime.fromisoformat(prev_time_str)
        else:
            prev_state, prev_time = "unknown", datetime.now()
else:
    prev_state, prev_time = "unknown", datetime.now()


current_state = check_status()
now = datetime.now()

if current_state != prev_state:
    duration = now - prev_time
    hours, remainder = divmod(int(duration.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    
    time_str = f"{hours} год. {minutes} хв." if hours > 0 else f"{minutes} хв."
    
    if current_state == "online":
        emoji = "🟢"
        msg = f"{emoji} СВІТЛО Є!\nБуло відсутнє: {time_str}"
    else:
        emoji = "🔴"
        msg = f"{emoji} СВІТЛО ЗНИКЛО\nБуло в наявності: {time_str}"
    
    send_tg_message(msg)
    
    with open(STATE_FILE, "w") as f:
        f.write(f"{current_state}|{now.isoformat()}")
    print(f"State changed to {current_state}")
else:
    print(f"State remains {current_state}. No action needed.")
