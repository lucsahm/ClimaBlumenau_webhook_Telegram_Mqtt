# Telegram Clima Bot

Bot do Telegram que responde a **/clima** e **/previsao_Xh** (OpenWeatherMap), usando **Flask** via **webhook**. A exposição pública é feita com **ngrok** e a orquestração local usa **tmux** (duas sessões: `webhook` e `ngrok`).

---

## 📢 Grupo no Telegram

Para facilitar testes, existe um grupo chamado **Clima Blumenau**.

**Link para entrar:** https://t.me/climablumenau

---

## ✨ Funcionalidades

- Comandos:
  - `/clima`
  - `/previsao_6h`
  - `/previsao_12h`
  - `/previsao_24h`
- Consulta à **OpenWeatherMap** (clima atual e previsão).
- Resposta formatada no Telegram.
- Publicação via **MQTT** (opcional).
- Recebe updates em tempo real via **webhook** (Flask).

---

## 🛠️ Tecnologias

- **Python 3**, **Flask**, **Requests**
- **Paho-MQTT** (opcional)
- **ngrok** (exposição pública)
- **tmux** (processos em background, inclusive em **Termux/Android**)

---

## 📁 Estrutura (resumo)

```bash
ClimaBlumenau_webhook_Telegram_Mqtt/
├─ README.md
├─ requirements.txt
├─ start_webhook.sh      # sobe Flask (tmux:webhook) + ngrok (tmux:ngrok) e registra o webhook
├─ webhook_clima.py      # Flask: endpoint /webhook -> despacha para os scripts
├─ clima_script.py       # Clima atual (OWM) -> Telegram/MQTT
├─ previsao_script.py    # Previsão (6/12/24h)
└─ notas.txt             # anotações internas
```

> **Importante:** o arquivo de configuração **não é versionado** (veja abaixo).

---

## 🔐 Configuração (`webhook.conf`)

Crie no **diretório do projeto** um arquivo não versionado `webhook.conf`:

```bash
# $HOME/ClimaBlumenau_webhook_Telegram_Mqtt/webhook.conf
# NÃO COMITAR!

# --- Telegram ---
export TELEGRAM_TOKEN="COLOQUE_AQUI_SEU_TOKEN"

# --- Flask / Webhook ---
export FLASK_PORT=5000
export SCRIPT_DIR="$HOME/ClimaBlumenau_webhook_Telegram_Mqtt"
export SCRIPT_CLIMA="$SCRIPT_DIR/webhook_clima.py"

# --- ngrok ---
export NGROK_REGION="sa"

# --- OpenWeatherMap ---
export OWM_API_KEY="COLOQUE_AQUI_SUA_CHAVE"
export CITY="Blumenau,BR"

# --- MQTT (opcional) ---
export MQTT_BROKER="broker.hivemq.com"
export MQTT_PORT="1883"
export MQTT_TOPIC="seu/topico"
# export MQTT_USER="se_precisar"
# export MQTT_PASS="se_precisar"
```

### .gitignore (essencial)

```bash
webhook.conf
webhook.config
__pycache__/
*.pyc
```

> Dica: para evitar problemas de fim de linha, considere um `.gitattributes`:
>
> ```
> *.sh  text eol=lf
> *.py  text eol=lf
> *.conf text eol=lf
> ```

---

## 📦 Dependências

**Python (pip):**

```bash
pip install -r requirements.txt
```

**Sistema (fora do pip):** `tmux`, `ngrok`, `python3`, `curl`

No Termux (Android), por exemplo:

```bash
pkg install tmux
```

Baixe o binário do **ngrok** e deixe no `PATH` (ou use o gerenciador da sua distro).

---

## ▶️ Como executar

### Método recomendado (automático)

1) Crie/preencha `webhook.conf`.

2) Dê permissão e execute:

```bash
chmod +x start_webhook.sh
./start_webhook.sh
```

O script:
- remove o webhook antigo no Telegram;
- **sobe o Flask numa sessão tmux (`webhook`) injetando as variáveis de ambiente diretamente no comando**;
- sobe o **ngrok** numa sessão tmux (`ngrok`) apontando para `FLASK_PORT` (5000 por padrão);
- obtém a URL pública do ngrok e registra o webhook do Telegram (`/webhook`).

**Ver a saída ao vivo (sem logs em arquivo):**

```bash
tmux attach -t webhook   # saída do Flask
tmux attach -t ngrok     # saída do ngrok
# para sair sem matar: Ctrl+b, depois d
```

### Alternativa manual (se necessário)

1) Carregue as variáveis:

```bash
source ./webhook.conf
```

2) Rode o Flask:

```bash
python3 webhook_clima.py --port "$FLASK_PORT"
```

3) Exponha e registre:

```bash
ngrok http "$FLASK_PORT" --region="$NGROK_REGION"
# copie a URL https pública do ngrok (ex.: https://abcd1234.ngrok-free.app)

curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook?url=https://abcd1234.ngrok-free.app/webhook"
```

---

## 🔧 Notas específicas

- `webhook_clima.py` despacha:
  - `/clima` → `clima_script.py <chat_id>`
  - `/previsao_6h|12h|24h` → `previsao_script.py <horas> <chat_id>`
- Os scripts Python leem configurações via **variáveis de ambiente** (definidas no `webhook.conf`).
- No Termux/Android, manter o **tmux** ajuda o sistema a não matar o processo em background.

---

## 🔒 Boas práticas

- **Nunca** comitar `webhook.conf`.
- Revogue tokens/keys se vazarem (BotFather / OWM).
- Em editores no Windows, use **LF** (ou rode `dos2unix`).

---

## ❓ Solução de problemas

- **`$'\r': comando não encontrado` ao carregar `webhook.conf`**
  - Converta para LF: `dos2unix webhook.conf`
  - Verifique: `file webhook.conf` (não deve mostrar `CRLF`).

- **`Variável de ambiente obrigatória não definida (OWM_API_KEY/...)`**
  - Confirme `source ./webhook.conf`.
  - Lembre: o `start_webhook.sh` injeta as variáveis **diretamente** no comando do Flask.

- **Nada chega no Telegram**
  - Veja `tmux attach -t webhook` (Flask) e `tmux attach -t ngrok`.
  - Reconfirme o webhook: `curl -s https://api.telegram.org/bot$TELEGRAM_TOKEN/getWebhookInfo`

- **Porta em uso**
  - Ajuste `FLASK_PORT` no `webhook.conf` (padrão 5000).
  - Mate sessões antigas: `tmux kill-session -t webhook`, `tmux kill-session -t ngrok`.

---

## ✅ Licença

Projeto pessoal/educacional. Adapte conforme necessário.
