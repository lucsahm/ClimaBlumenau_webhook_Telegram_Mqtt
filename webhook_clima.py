from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # 1. Obtém os dados da requisição
    data = request.get_json()
    message = data.get("message", {}).get("text", "")
    chat_id = data.get("message", {}).get("chat", {}).get("id")

    # 2. Ignora requisições sem mensagem ou chat_id
    if not message or not chat_id:
        return "Ignored", 200

    # 3. Normaliza a mensagem para comparação
    message = message.strip().lower()

    # 4. Verifica qual comando foi enviado e chama o script correspondente
    if message == "/clima@nome_bot":
        subprocess.Popen(["python", "clima_script.py", str(chat_id)])
    
    elif message == "/previsao_6h@nome_bot":
        # Argumentos: o número de horas e o chat_id
        subprocess.Popen(["python", "previsao_script.py", "6", str(chat_id)])

    elif message == "/previsao_12h@nome_bot":
        subprocess.Popen(["python", "previsao_script.py", "12", str(chat_id)])

    elif message == "/previsao_24h@nome_bot":
        subprocess.Popen(["python", "previsao_script.py", "24", str(chat_id)])
    
    # 5. A função retorna "OK" apenas uma vez, no final
    # Isso garante que todos os 'if/elif's sejam verificados
    return "OK", 200

if __name__ == "__main__":
    # Configura o app para rodar em todas as interfaces na porta 5001
    app.run(host="0.0.0.0", port=5001)
