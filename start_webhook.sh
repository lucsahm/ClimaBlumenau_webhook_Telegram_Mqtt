#!/usr/bin/env bash
# $HOME/Scripts/ClimaBlumenau_webhook_Telegram_Mqtt/start_webhook.sh
set -Eeuo pipefail

CONFIG_FILE="$HOME/Scripts/ClimaBlumenau_webhook_Telegram_Mqtt/webhook.conf"
[[ -f "$CONFIG_FILE" ]] || { echo "[ERRO] Config não encontrada: $CONFIG_FILE"; exit 1; }

# shellcheck source=/dev/null
source "$CONFIG_FILE"

need_bin() { command -v "$1" >/dev/null 2>&1 || { echo "[ERRO] binário não encontrado: $1"; exit 1; }; }
need_bin tmux
need_bin curl
need_bin ngrok
need_bin python3

# Checagem mínima de variáveis essenciais
: "${TELEGRAM_TOKEN:?[ERRO] TELEGRAM_TOKEN não definido no webhook.conf}"
: "${SCRIPT_CLIMA:?[ERRO] SCRIPT_CLIMA não definido no webhook.conf}"
: "${FLASK_PORT:?[ERRO] FLASK_PORT não definido no webhook.conf}"
: "${NGROK_REGION:?[ERRO] NGROK_REGION não definido no webhook.conf}"

# ========================
# REMOVER WEBHOOK ANTIGO
# ========================
echo "[INFO] Removendo webhook antigo..."
curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/deleteWebhook" >/dev/null || true
echo -e "[OK] Webhook antigo removido.\n"

# ========================
# INICIAR TMUX WEBHOOK (FLASK)
# ========================
echo "[INFO] Iniciando sessão tmux para webhook..."
tmux kill-session -t webhook 2>/dev/null || true

[[ -f "$SCRIPT_CLIMA" ]] || { echo "[ERRO] Script não encontrado: $SCRIPT_CLIMA"; exit 1; }

# Passa a porta; tmux herda todas as variáveis que já exportamos acima
echo "[DEBUG] tmux new-session -d -s webhook \"$SCRIPT_CLIMA --port $FLASK_PORT\""
tmux kill-session -t webhook 2>/dev/null || true
tmux new-session -d -s webhook "\
TELEGRAM_TOKEN='${TELEGRAM_TOKEN-}' \
OWM_API_KEY='${OWM_API_KEY-}' \
CITY='${CITY-}' \
MQTT_BROKER='${MQTT_BROKER-}' \
MQTT_PORT='${MQTT_PORT-}' \
MQTT_TOPIC='${MQTT_TOPIC-}' \
MQTT_USER='${MQTT_USER-}' \
MQTT_PASS='${MQTT_PASS-}' \
SCRIPT_DIR='${SCRIPT_DIR-}' \
FLASK_PORT='${FLASK_PORT-}' \
NGROK_REGION='${NGROK_REGION-}' \
\"$SCRIPT_CLIMA\" --port \"${FLASK_PORT-}\""

sleep 1
tmux has-session -t webhook 2>/dev/null && echo "[OK] Sessão 'webhook' criada." || { echo "[ERRO] Falha ao criar 'webhook'"; exit 1; }

# ========================
# INICIAR TMUX NGROK
# ========================
echo "[INFO] Iniciando sessão tmux para ngrok..."
tmux kill-session -t ngrok 2>/dev/null || true
tmux new-session -d -s ngrok "ngrok http $FLASK_PORT --region=$NGROK_REGION"

# Aguarda o ngrok inicializar (até 10s)
for i in {1..10}; do
  sleep 1
  NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels \
    | grep -o 'https://[^"]*\.ngrok-free\.app' | head -n 1 || true)
  [[ -n "${NGROK_URL:-}" ]] && break
done

[[ -n "${NGROK_URL:-}" ]] || { echo "[ERRO] Não foi possível capturar a URL do ngrok. Veja: tmux attach -t ngrok"; exit 1; }
echo "[OK] URL do ngrok: $NGROK_URL"

# ========================
# DEFINIR NOVO WEBHOOK
# ========================
echo "[INFO] Configurando novo webhook..."
curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook?url=${NGROK_URL}/webhook" >/dev/null \
  && echo "[OK] Webhook atualizado."

echo
echo "======================================="
echo "[SUCESSO] Tudo pronto!"
echo "Webhook: ${NGROK_URL}/webhook"
echo "Tmux sessions:"
echo " - webhook"
echo " - ngrok"
echo
echo "Logs:"
echo "    tmux attach -t webhook"
echo "    tmux attach -t ngrok"
echo "======================================="
