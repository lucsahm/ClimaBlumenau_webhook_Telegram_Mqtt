from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message", {}).get("text", "")
    chat_id = data.get("message", {}).get("chat", {}).get("id")

    if message.strip().lower() == "/clima" and chat_id:                      #https://api.telegram.org/bot<CHAVEDOBOT>/getUpdates para verificar qual a palavra do codigo correta
        subprocess.Popen(["python", "clima_script.py", str(chat_id)])
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
