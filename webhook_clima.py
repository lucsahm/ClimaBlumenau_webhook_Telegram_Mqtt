#!/usr/bin/env python3
# $HOME/Scripts/ClimaBlumenau_webhook_Telegram_Mqtt/webhook_clima.py

from flask import Flask, request
import subprocess
import os
import argparse

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message", {}) or {}).get("text", "")
    chat_id = (data.get("message", {}) or {}).get("chat", {}).get("id")

    if not msg or not chat_id:
        return "Ignored", 200

    msg = msg.strip().lower()

    if msg in ("/clima", "/clima@sahm2_bot"):
        subprocess.Popen(["python3", "clima_script.py", str(chat_id)])

    elif msg in ("/previsao_6h", "/previsao_6h@sahm2_bot"):
        subprocess.Popen(["python3", "previsao_script.py", "6", str(chat_id)])

    elif msg in ("/previsao_12h", "/previsao_12h@sahm2_bot"):
        subprocess.Popen(["python3", "previsao_script.py", "12", str(chat_id)])

    elif msg in ("/previsao_24h", "/previsao_24h@sahm2_bot"):
        subprocess.Popen(["python3", "previsao_script.py", "24", str(chat_id)])

    return "OK", 200

def _get_port():
    # 1) --port tem prioridade
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--port", type=int, default=None)
    args, _ = parser.parse_known_args()

    if args.port:
        return args.port

    # 2) FLASK_PORT do ambiente; fallback para 5000
    return int(os.getenv("FLASK_PORT", "5000"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=_get_port())
