#!/usr/bin/env python3
# $HOME/Scripts/ClimaBlumenau_webhook_Telegram_Mqtt/webhook_clima.py
from flask import Flask, request
import subprocess
import os
import argparse
import sys

app = Flask(__name__)

SCRIPT_DIR = os.getenv("SCRIPT_DIR") or os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable or "python3"

def _abs(path):  # garante caminhos absolutos
    return path if os.path.isabs(path) else os.path.join(SCRIPT_DIR, path)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or {}).get("text") or ""
    chat_id = ((data.get("message") or {}).get("chat") or {}).get("id")

    if not msg or not chat_id:
        return "Ignored", 200

    msg = msg.strip().lower()
    clima_py = _abs("clima_script.py")
    previsao_py = _abs("previsao_script.py")

    if msg in ("/clima", "/clima@bot_name"):
        subprocess.Popen([PYTHON, clima_py, str(chat_id)], cwd=SCRIPT_DIR)

    elif msg in ("/previsao_6h", "/previsao_6h@bot_name"):
        subprocess.Popen([PYTHON, previsao_py, "6", str(chat_id)], cwd=SCRIPT_DIR)

    elif msg in ("/previsao_12h", "/previsao_12h@bot_name"):
        subprocess.Popen([PYTHON, previsao_py, "12", str(chat_id)], cwd=SCRIPT_DIR)

    elif msg in ("/previsao_24h", "/previsao_24h@bot_name"):
        subprocess.Popen([PYTHON, previsao_py, "24", str(chat_id)], cwd=SCRIPT_DIR)

    return "OK", 200

def _get_port():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--port", type=int, default=None)
    args, _ = parser.parse_known_args()
    if args.port:
        return args.port
    return int(os.getenv("FLASK_PORT", "5000"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=_get_port())
