#!/usr/bin/env python3
# $HOME/Scripts/ClimaBlumenau_webhook_Telegram_Mqtt/clima_script.py
import os
import sys
import json
import requests
import paho.mqtt.client as mqtt

# --------- Config por ENV (webhook.conf) ----------
OWM_API_KEY   = os.getenv("OWM_API_KEY")
CITY          = os.getenv("CITY", "Blumenau,BR")
TELEGRAM_TOKEN= os.getenv("TELEGRAM_TOKEN")

MQTT_BROKER   = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT     = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC    = os.getenv("MQTT_TOPIC", "seu/topico")
MQTT_USER     = os.getenv("MQTT_USER", "")
MQTT_PASS     = os.getenv("MQTT_PASS", "")

# --------- Helpers ----------
def require(var_name, value):
    if not value:
        print(f"[ERRO] Variável de ambiente obrigatória não definida: {var_name}")
        sys.exit(1)

require("OWM_API_KEY", OWM_API_KEY)
require("TELEGRAM_TOKEN", TELEGRAM_TOKEN)

def obter_dados_clima():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": CITY, "appid": OWM_API_KEY, "units": "metric", "lang": "pt_br"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        velocidade_vento_ms = (data.get("wind") or {}).get("speed", 0.0)
        velocidade_vento_kmh = round(float(velocidade_vento_ms) * 3.6, 1)

        return {
            "cidade": data.get("name", CITY),
            "temperatura": (data.get("main") or {}).get("temp"),
            "sensacao": (data.get("main") or {}).get("feels_like"),
            "umidade": (data.get("main") or {}).get("humidity"),
            "vento": velocidade_vento_kmh,  # número
            "descricao": ((data.get("weather") or [{}])[0]).get("description", "")
        }
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao obter clima: {e}")
        return None

def publicar_mqtt(payload: dict):
    try:
        client = mqtt.Client()
        if MQTT_USER:
            client.username_pw_set(MQTT_USER, MQTT_PASS or None)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        msg = json.dumps(payload, ensure_ascii=False)
        res = client.publish(MQTT_TOPIC, msg, qos=1)
        res.wait_for_publish()
        client.loop_stop()
        client.disconnect()
        print(f"[OK] Publicado em '{MQTT_TOPIC}': {msg}")
    except Exception as e:
        print(f"[WARN] MQTT publish falhou: {e}")

def enviar_telegram(chat_id: str, payload: dict):
    texto = (
        f"🌤 Clima em {payload['cidade']}:\n"
        f"🌡 Temperatura: {payload['temperatura']}°C\n"
        f"🤒 Sensação: {payload['sensacao']}°C\n"
        f"💧 Umidade: {payload['umidade']}%\n"
        f"💨 Vento: {payload['vento']} km/h\n"
        f"🔎 Descrição: {payload['descricao'].capitalize()}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": chat_id, "text": texto, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=params, timeout=10)
        r.raise_for_status()
        print("[OK] Mensagem enviada ao Telegram.")
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao enviar para Telegram: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python clima_script.py <chat_id>")
        sys.exit(1)
    chat_id = sys.argv[1]
    dados = obter_dados_clima()
    if dados:
        publicar_mqtt(dados)
        enviar_telegram(chat_id, dados)
