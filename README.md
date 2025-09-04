# Telegram Clima Bot

Bot do Telegram que responde a comandos como **/clima** e **/previsao_Xh** com dados meteorológicos (OpenWeatherMap), usando **Flask** via **webhook**. A exposição pública é feita com **ngrok** e a orquestração local usa **tmux** (duas sessões: `webhook` e `ngrok`).

---

## 📢 Grupo no Telegram

Para facilitar testes, existe um grupo chamado **Clima Blumenau**.

**Link para entrar:** https://t.me/climablumenau  

---

## ✨ Funcionalidades

- Comandos no Telegram:
  - `/clima`
  - `/previsao_6h`
  - `/previsao_12h`
  - `/previsao_24h`
- Consulta a **OpenWeatherMap** para clima atual/previsão.
- Envia resposta formatada ao chat que solicitou.
- Publica via **MQTT** (opcional).
- Recebe atualizações do Telegram em tempo real via **webhook** (Flask).

---

## 🛠️ Tecnologias

- **Python 3**
- **Flask** (webhook)
- **Requests** (HTTP)
- **Paho-MQTT** (opcional)
- **ngrok** (expor local para internet)
- **tmux** (processos rodando em background)

---

## 📁 Estrutura dos arquivos (relevantes)
````bash
ClimaBlumenau_webhook_Telegram_Mqtt/
├─ README.md
├─ requirements.txt
├─ start_webhook.sh # sobe Flask (tmux: webhook) + ngrok (tmux: ngrok) e configura o webhook
├─ webhook_clima.py # Flask: endpoint /webhook -> despacha para os scripts
├─ clima_script.py # Clima atual (usa OWM e envia ao Telegram / MQTT)
├─ previsao_script.py # Previsão em horas (6/12/24)
└─ notas.txt # Anotações internas
````

> **Importante:** o arquivo de configuração **não é versionado** por segurança (ver seção abaixo).

---

## 🔐 Configuração (arquivo **`webhook.conf`** / *também chamado de* `webhook.config`)

Crie no diretório do projeto um arquivo **não versionado** chamado `webhook.conf` (se preferir o nome `webhook.config`, adapte os comandos do seu ambiente). Exemplo:

```bash
# webhook.conf  (NÃO comitar)
export TELEGRAM_TOKEN="COLE_AQUI_SEU_TOKEN_DO_BOT"
export FLASK_PORT=5001
export SCRIPT_CLIMA="$HOME/ClimaBlumenau_webhook_Telegram_Mqtt/webhook_clima.py"
export NGROK_REGION="sa"   # South America
# (opcional) export OWM_API_KEY="SUA_CHAVE_OPENWEATHERMAP"
# (opcional) export MQTT_BROKER="tcp://host:1883"
# (opcional) export MQTT_TOPIC="clima/blumenau"
````

# Não suba este arquivo para o Git. Adicione ao .gitignore:

````bash
webhook.conf
webhook.config
flask.log
__pycache__/
*.pyc
````

---

## 📦 Dependências

# Python (pip)

Instale as libs do projeto:

pip install -r requirements.txt

# Sistema (não vão no requirements.txt)

	*tmux
	*ngrok
	*python3 (intérprete)

No Termux (Android), por exemplo:
````bash
pkg install tmux
````

Baixe o binário do ngrok e deixe no PATH (ou use o gerenciador da sua distro).

---

## ▶️ Como executar

# Método recomendado (automatizado)

1. Garanta que o webhook.conf foi criado e preenchido.

2. Dê permissão e execute o script:
````bash
chmod +x start_webhook.sh
./start_webhook.sh
````

O script:

* remove webhook antigo no Telegram,
* sobe Flask em tmux (sessão webhook) na porta definida (FLASK_PORT),
* sobe ngrok em tmux (sessão ngrok) apontando para a mesma porta,
* captura a URL pública HTTPS do ngrok,
* registra o webhook no Telegram (/webhook).

# Logs (quando quiser ver):

````bash
tmux attach -t webhook   # saída do Flask
tmux attach -t ngrok     # saída do ngrok
# para sair sem
 matar: Ctrl+b, depois d
````

# Alternativa manual (somente se necessário)

1. Rodar Flask diretamente:

````bash
export FLASK_PORT=5001
python3 webhook_clima.py  # ou: python3 webhook_clima.py --port 5001
````

2. Expor com ngrok e registrar o webhook:

````bash
ngrok http 5001 --region=sa
# copie a URL https pública do ngrok, ex: https://abcd1234.ngrok-free.app

curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook?url=https://abcd1234.ngrok-free.app/webhook"
````

---

## 🔧 Configurações específicas dos scripts

* clima_script.py
	* Use sua chave OpenWeatherMap (OWM_API_KEY) e defina a cidade (ex.: Blumenau,BR).
	*Pode usar variáveis de ambiente ou constantes no próprio script (conforme sua implementação atual).

* previsao_script.py
	*Recebe como argumento o número de horas (6, 12 ou 24) + chat_id.
Obs.: O webhook_clima.py despacha conforme o texto do comando recebido no Telegram.

---

## 🔒 Boas práticas de segurança

* Nunca comitar webhook.conf / webhook.config (contém token do bot e chaves).
* Se um token vazar, gere um novo no BotFather e remova o antigo.
* Evite deixar logs sensíveis versionados (ex.: flask.log).

---

## ❓ Solução de problemas

* Não recebo mensagens do Telegram
	* Confira se o ngrok está ativo e a URL pública está registrada como webhook.
	* Verifique a sessão tmux do Flask: tmux attach -t webhook.
* Porta em uso / conflito
	* Ajuste FLASK_PORT no webhook.conf.
	* Mate sessões antigas: tmux kill-session -t webhook, tmux kill-session -t ngrok.
* Erros de dependências
	* Reinstale: pip install -r requirements.txt.

---

## ✅ Licença

Projeto de uso pessoal/educacional. Adapte conforme sua necessidade.