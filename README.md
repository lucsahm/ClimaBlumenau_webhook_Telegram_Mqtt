## 📢 Grupo no Telegram

Para facilitar testes, tirar dúvidas e trocar ideias, existe um grupo no Telegram chamado **Clima Blumenau**.

Você pode participar para receber atualizações, enviar comandos e interagir com o bot em um ambiente real.

**Link para entrar no grupo:** https://t.me/climablumenau

# Telegram Clima Bot

Este projeto cria um bot Telegram que responde ao comando `/clima` enviando informações meteorológicas atuais para um grupo ou chat, utilizando a API do OpenWeatherMap. A comunicação é feita via webhook com Flask e o bot pode publicar dados também via MQTT.

---

## Funcionalidades

- Recebe o comando `/clima` no Telegram.
- Consulta a API do OpenWeatherMap para obter dados meteorológicos atuais.
- Envia a resposta formatada para o grupo ou usuário que solicitou.
- Publica os dados via MQTT (opcional).
- Utiliza webhook para receber atualizações do Telegram em tempo real.

---

## Tecnologias usadas

- Python 3
- Flask (para o webhook)
- Requests (para chamadas HTTP)
- Paho-MQTT (para MQTT)
- Ngrok (para expor localmente o webhook para internet)

---

## Configuração

### 1. Criar bot no Telegram

- Fale com o [@BotFather](https://t.me/BotFather) e crie um novo bot.
- Anote o token gerado.

### 2. Configurar webhook

- Execute seu servidor Flask (arquivo `webhook.py`), que ficará escutando as requisições.
- Use o [ngrok](https://ngrok.com/) para expor seu servidor local para a internet:

  ```bash
  ngrok http 5000
  ```
Copie a URL pública HTTPS gerada, por exemplo:  
`https://abcd1234.ngrok.io`

Registre a URL do webhook no Telegram, ajustando para o endpoint correto (`/webhook`):

  ```bash
`https://api.telegram.org/bot<SEU_TOKEN>/setWebhook?url=https://abcd1234.ngrok.io/webhook`
```

### 3. Configurar variáveis no `clima_script.py`

- Insira sua chave da OpenWeatherMap (`OWM_API_KEY`)
- Defina a cidade desejada (exemplo: `Blumenau,BR`)
- Configure o token do bot Telegram (`TELEGRAM_BOT_TOKEN`)
- Configure o chat ID (`TELEGRAM_CHAT_ID`) — normalmente obtido via webhook

---

### Executando localmente

Instale as dependências:

```bash
pip install -r requirements.txt
python webhook.py
ngrok http 5000
```

Envie /clima para o seu bot no Telegram. O bot responderá com as informações do clima atual.

Estrutura dos arquivos
webhook.py — servidor Flask que recebe atualizações do Telegram e chama o script do clima.

clima_script.py — script que consulta a API de clima e envia mensagem ao Telegram e MQTT.

requirements.txt — lista de dependências Python.
