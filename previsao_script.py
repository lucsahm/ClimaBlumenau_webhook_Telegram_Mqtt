#!/usr/bin/env python3
# $HOME/Scripts/ClimaBlumenau_webhook_Telegram_Mqtt/previsao_script.py
import os
import sys
import requests

API_KEY        = os.getenv("OWM_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CITY           = os.getenv("CITY", "Blumenau,BR")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def require(var_name, value):
    if not value:
        print(f"[ERRO] Variável obrigatória não definida: {var_name}")
        sys.exit(1)

require("OWM_API_KEY", API_KEY)
require("TELEGRAM_TOKEN", TELEGRAM_TOKEN)

def obter_previsao(horas: int) -> str:
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": CITY, "appid": API_KEY, "units": "metric", "lang": "pt_br"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "list" not in data:
            return "Erro: dados de previsão não encontrados."

        linhas = []
        blocos = min(horas // 3, len(data["list"]))
        for i in range(blocos):
            bloco = data["list"][i]
            hora = bloco.get("dt_txt", "")[11:16]
            main = bloco.get("main", {})
            weather = (bloco.get("weather") or [{}])[0]
            wind = bloco.get("wind", {})
            vento_kmh = float(wind.get("speed", 0.0)) * 3.6

            linhas.append(
                f"<b>Horário:</b> {hora}\n"
                f"🌡️ Temp: {main.get('temp', 0):.1f}°C (sens. {main.get('feels_like', 0):.1f}°C)\n"
                f"☁️ Condição: {weather.get('description','').capitalize()}\n"
                f"💧 Umidade: {main.get('humidity','?')}%\n"
                f"💨 Vento: {vento_kmh:.1f} km/h\n"
                f"--------------------"
            )
        return "\n".join(linhas).strip()
    except requests.RequestException as e:
        return f"Erro ao obter previsão do OpenWeatherMap: {e}"

def enviar_previsao_telegram(chat_id: str, texto_previsao: str) -> bool:
    params = {"chat_id": chat_id, "text": texto_previsao, "parse_mode": "HTML"}
    try:
        r = requests.post(TELEGRAM_API_URL, data=params, timeout=10)
        r.raise_for_status()
        print("[OK] Previsão enviada ao Telegram.")
        return True
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao enviar previsão ao Telegram: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: ./previsao_script.py <horas> <chat_id>")
        sys.exit(1)
    try:
        horas = int(sys.argv[1])
        chat_id = sys.argv[2]
    except ValueError:
        print("Erro: <horas> deve ser inteiro (6, 12, 24).")
        sys.exit(1)

    if horas not in (6, 12, 24):
        enviar_previsao_telegram(chat_id, "Erro: peça 6h, 12h ou 24h.")
        sys.exit(1)

    previsao = obter_previsao(horas)
    mensagem = f"Previsão para as próximas {horas}h em {CITY}:\n\n{previsao}"
    enviar_previsao_telegram(chat_id, mensagem)
