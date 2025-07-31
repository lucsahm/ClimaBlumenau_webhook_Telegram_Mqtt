import requests
import sys
from datetime import datetime

# --- CONFIGURAÇÕES ---
# Suas chaves de API. Recomendo usar variáveis de ambiente ou um arquivo de configuração
# para chaves sensíveis em vez de codificá-las diretamente no script.
API_KEY = "SUACHAVE"
BOT_TOKEN = "BOTTOKEN"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

CITY = "Blumenau"

# --- FUNÇÃO obter_previsao ---
def obter_previsao(horas):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": CITY,
        "appid": API_KEY,
        "units": "metric",
        "lang": "pt_br"
    }

    try: # Adicionei um try-except para a requisição da API
        response = requests.get(url, params=params)
        response.raise_for_status() # Levanta exceção para erros HTTP
        data = response.json()

        if "list" not in data:
            return "Erro: dados de previsão não encontrados na resposta da API."

        texto_previsao_linhas = []
        # Certifique-se de que blocos não excede o número de elementos em data["list"]
        blocos = min(horas // 3, len(data["list"]))
        
        for i in range(blocos):
            bloco = data["list"][i]
            dt_txt = bloco["dt_txt"]
            # A hora da API é UTC. Se quiser local de Blumenau (GMT-3), precisa converter.
            # Por simplicidade, mantive o fuso horário da string da API.
            hora = dt_txt[11:16] # Pega apenas HH:MM

            temp = bloco["main"]["temp"]
            sensacao = bloco["main"]["feels_like"]
            descricao = bloco["weather"][0]["description"]
            umidade = bloco["main"]["humidity"]
            vento_ms = bloco["wind"]["speed"]
            vento_kmh = vento_ms * 3.6 # Converte m/s para km/h

            texto_previsao_linhas.append(
                f"<b>Horário:</b> {hora}\n"
                f"🌡️ Temperatura: {temp:.1f}°C (sensação {sensacao:.1f}°C)\n"
                f"☁️ Condição: {descricao.capitalize()}\n"
                f"💧 Umidade: {umidade}%\n"
                f"💨 Vento: {vento_kmh:.1f} km/h\n"
                "--------------------" # Separador para cada previsão
            )

        return "\n".join(texto_previsao_linhas).strip()
    
    except requests.exceptions.RequestException as e:
        return f"Erro de conexão ao obter previsão do OpenWeatherMap: {e}"
    except Exception as e:
        return f"Erro inesperado ao processar dados da previsão: {e}"


# --- FUNÇÃO DE ENVIO PARA O TELEGRAM (AGORA NO NÍVEL CORRETO DE INDENTAÇÃO) ---
def enviar_previsao_telegram(chat_id, texto_previsao):
    url = TELEGRAM_API_URL
    params = {
        "chat_id": chat_id,
        "text": texto_previsao,
        "parse_mode": "HTML" # Verifique se seu texto contém HTML. Caso contrário, remova ou use "MarkdownV2".
    }

    try:
        response = requests.post(url, data=params)
        response.raise_for_status() # Levanta exceção para erros HTTP (4xx ou 5xx)
        print("Mensagem de previsão enviada ao Telegram com sucesso.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem de previsão para o Telegram: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Resposta de erro do Telegram: {e.response.text}")
        return False

# --- EXECUÇÃO PRINCIPAL DO SCRIPT ---
if __name__ == "__main__":
    # O script espera 3 argumentos: [nome_do_script, horas, chat_id]
    if len(sys.argv) != 3:
        print("Uso: ./previsao_script.py <horas> <chat_id>")
        sys.exit(1)

    try:
        horas = int(sys.argv[1]) # O primeiro argumento é o número de horas (ex: 6, 12, 24)
        chat_id = sys.argv[2]    # O segundo argumento é o ID do chat do Telegram
    except ValueError:
        print("Erro: O número de horas deve ser um inteiro.")
        # É uma boa prática enviar essa mensagem de erro para o Telegram também, se possível
        sys.exit(1)

    if horas not in [6, 12, 24]:
        # Envia a mensagem de erro para o Telegram
        enviar_previsao_telegram(chat_id, "Erro: Por favor, solicite a previsão para 6h, 12h ou 24h.")
        sys.exit(1)

    # 1. Obtém o texto da previsão (já vem formatado)
    previsao_detalhada = obter_previsao(horas)
    
    # 2. Constrói a mensagem final completa para o usuário
    mensagem_final_para_telegram = f"Previsão para as próximas {horas} horas em {CITY}:\n\n{previsao_detalhada}"

    # 3. Envia a mensagem completa para o Telegram
    enviar_previsao_telegram(chat_id, mensagem_final_para_telegram)
