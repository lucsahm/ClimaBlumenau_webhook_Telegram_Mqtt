#!/usr/bin/env python

import requests
import json
import paho.mqtt.client as mqtt
import sys

# CONFIGURAÇÕES
OWM_API_KEY = '2db226f533e52c42dc179f1ec8de42d2'  # <- Insira sua chave da OpenWeatherMap (vem por email)
CITY = 'Blumenau,BR'
MQTT_BROKER = 'broker.hivemq.com' # seu broker
MQTT_PORT = 1883
MQTT_TOPIC = 'blunenau/clima' # seu topico MQTT

TELEGRAM_BOT_TOKEN = '8208784836:AAHpLzslU93Pf49QaY6-WKvbuD72KYCgMq8' # https://api.telegram.org/bot<CHAVEDOBOT>/getUpdates para verificar qual a palavra do codigo correta

def obter_dados_clima():
    url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OWM_API_KEY}&units=metric&lang=pt_br'
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print("Erro ao buscar dados do clima:", data)
        return None

    velocidade_vento_ms = data['wind']['speed']
    # Converte m/s para km/h (1 m/s = 3.6 km/h)
    velocidade_vento_kmh = round(velocidade_vento_ms * 3.6, 2) # Arredonda para 2 casas decimais

    clima = {
        'cidade': data.get('name'),
        'temperatura': data['main']['temp'],
        'sensacao': data['main']['feels_like'],
        'umidade': data['main']['humidity'],
        'vento': f"{velocidade_vento_kmh} km/h",
        'descricao': data['weather'][0]['description']
    }

    return clima

def publicar_mqtt(payload):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    mensagem = json.dumps(payload, ensure_ascii=False)
    client.publish(MQTT_TOPIC, mensagem,qos=1)
    print(f'Publicado em {MQTT_TOPIC}: {mensagem}')

    client.loop_stop()
    client.disconnect()

def enviar_telegram(chat_id, payload):
    texto = (
        f"🌤 Clima em {payload['cidade']}:\n"
        f"🌡 Temperatura: {payload['temperatura']}°C\n"
        f"🤒 Sensação: {payload['sensacao']}°C\n"
        f"💧 Umidade: {payload['umidade']}%\n"
        f"💨 Vento: {payload['vento']} kmh\n"
        f"🔎 Descrição: {payload['descricao'].capitalize()}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "HTML"
    }

    response = requests.post(url, data=params)
    if response.status_code == 200:
        print("Mensagem enviada ao Telegram com sucesso.")
    else:
        print("Erro ao enviar mensagem para o Telegram:", response.text)

# EXECUÇÃO DIRETA
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python clima_script.py <chat_id>")
        sys.exit(1)

    chat_id = sys.argv[1]

    dados = obter_dados_clima()
    if dados:
        publicar_mqtt(dados)
        enviar_telegram(chat_id, dados)
