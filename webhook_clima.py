#!/usr/bin/env python3
# $HOME/Scripts/ClimaBlumenau_webhook_Telegram_Mqtt/webhook_clima.py

from flask import Flask, request
import subprocess, os, argparse, sys

app = Flask(__name__)

# Diretório base dos scripts (do env SCRIPT_DIR ou pasta deste arquivo)
SCRIPT_DIR = os.getenv("SCRIPT_DIR") or os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable or "python3"

def _abs(path: str) -> str:
    """Garante caminho absoluto a partir de SCRIPT_DIR."""
    return path if os.path.isabs(path) else os.path.join(SCRIPT_DIR, path)

def _normalize_cmd(text: str) -> str:
    """Converte '/clima@bot' -> '/clima' e ignora o que vier depois de espaço."""
    if not text:
        return ""
    tok = text.strip().lower().split()[0]
    return tok.split('@', 1)[0]

def _spawn(script_name: str, *args):
    """Executa o script Python com cwd=SCRIPT_DIR, herdando as variáveis do ambiente."""
    script_path = _abs(script_name)
    env = os.environ.copy()  # já contém TELEGRAM_TOKEN do webhook.conf (via start_webhook.sh)
    subprocess.Popen([PYTHON, script_path, *map(str, args)], cwd=SCRIPT_DIR, env=env)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    msg = ((data.get("message") or {}).get("text") or "")
    chat_id = ((data.get("message") or {}).get("chat") or {}).get("id")

    if not msg or not chat_id:
        return "Ignored", 200

    cmd = _normalize_cmd(msg)

    if cmd == "/clima":
        _spawn("clima_script.py", str(chat_id))
    elif cmd == "/previsao_6h":
        _spawn("previsao_script.py", "6", str(chat_id))
    elif cmd == "/previsao_12h":
        _spawn("previsao_script.py", "12", str(chat_id))
    elif cmd == "/previsao_24h":
        _spawn("previsao_script.py", "24", str(chat_id))

    return "OK", 200

def _get_port():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--port", type=int, default=None)
    args, _ = parser.parse_known_args()
    return args.port or int(os.getenv("FLASK_PORT", "5000"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=_get_port())
