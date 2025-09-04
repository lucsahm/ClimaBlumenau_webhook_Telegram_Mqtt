#!/bin/bash

# $HOME/Scripts/ClimaBlumenau_webhook_Telegram_Mqtt/start_webhook.sh

# set -x  # Ativa o modo debug, vai mostrar todos os comandos sendo executados
# ===========================================
# SCRIPT DE AUTOMATIZAÇÃO DO WEBHOOK TELEGRAM
# ===========================================

# Carregar variáveis do arquivo de configuração
CONFIG_FILE="$HOME/ClimaBlumenau_webhook_Telegram_Mqtt/webhook.conf"
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "[ERRO] Arquivo de configuração não encontrado: $CONFIG_FILE"
    exit 1
fi

# Carrega e EXPORTA as variáveis (já exportadas no .conf)
# shellcheck source=/dev/null
source "$CONFIG_FILE"

# ========================
# REMOVER WEBHOOK ANTIGO
# ========================
echo "[INFO] Removendo webhook antigo..."
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/deleteWebhook" >/dev/null
echo -e "[OK] Webhook antigo removido.\n"

# ========================
# INICIAR TMUX WEBHOOK (FLASK)
# ========================
echo "[INFO] Iniciando sessão tmux para webhook..."
tmux kill-session -t webhook 2>/dev/null || true

if [[ ! -f "$SCRIPT_CLIMA" ]]; then
  echo "[ERRO] Script não encontrado: $SCRIPT_CLIMA"
  exit 1
fi

# Passa a porta explicitamente (também disponível via env)
echo "[DEBUG] Rodando: tmux new-session -d -s webhook \"$SCRIPT_CLIMA --port $FLASK_PORT\""
tmux new-session -d -s webhook "$SCRIPT_CLIMA --port $FLASK_PORT"
echo "[OK] Sessão 'webhook' iniciada."

sleep 1
if tmux has-session -t webhook 2>/dev/null; then
  echo "[OK] Sessão 'webhook' criada com sucesso."
else
  echo "[ERRO] Falha ao criar a sessão 'webhook'. Veja: tmux attach -t webhook"
  exit 1
fi

# ========================
# INICIAR TMUX NGROK
# ========================
echo "[INFO] Iniciando sessão tmux para ngrok..."
tmux kill-session -t ngrok 2>/dev/null || true
tmux new-session -d -s ngrok "ngrok http $FLASK_PORT --region=$NGROK_REGION"

# Aguarda o ngrok inicializar
sleep 5

# ========================
# PEGAR URL HTTPS DO NGROK
# ========================
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels \
  | grep -o 'https://[^"]*\.ngrok-free\.app' \
  | head -n 1)

if [[ -z "$NGROK_URL" ]]; then
  echo "[ERRO] Não foi possível capturar a URL do ngrok!"
  echo "Verifique: tmux attach -t ngrok"
  exit 1
fi
echo "[OK] URL do ngrok: $NGROK_URL"

# ========================
# DEFINIR NOVO WEBHOOK
# ========================
echo "[INFO] Configurando novo webhook..."
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook?url=$NGROK_URL/webhook" >/dev/null
echo "[OK] Webhook atualizado."

echo
echo "======================================="
echo "[SUCESSO] Tudo pronto!"
echo "Webhook: $NGROK_URL/webhook"
echo "Tmux sessions:"
echo " - webhook"
echo " - ngrok"
echo
echo "Logs:"
echo "    tmux attach -t webhook"
echo "    tmux attach -t ngrok"
echo "======================================="

