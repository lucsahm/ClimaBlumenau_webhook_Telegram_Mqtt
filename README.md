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

### 2. Crie um grupo no Telegram
  - Adicione o bot que foi criado ao grupo
  - Envie uma mensagem qualquer
  - Acesse no navegador
    `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
  - Procure pelo chatId que noramalmente começa com sinal de '-': '-123456789'

### 3. Configurar webhook

  - Instale o webhook conforme seu ambiente e copie seu token.
    `https://dashboard.ngrok.com`
  
  - Execute o comando no terminal:
    ```bash
    ngrok config add-authtoken <SEU_TOKEN>
    ```
  - Execute seu servidor Flask (arquivo `webhook.py`), que ficará escutando as requisições.
  
  - Inicialize o ngrok na porta 5000 (ou outra) mas tem que verificar se vai ser a mesma do Flask
    ```bash
    ngrok http 5000
    ```
  - Copie a URL pública HTTPS gerada pelo ngrok, por exemplo:  
    `https://abcd1234.ngrok.io`

  - Registre a URL do webhook no Telegram, ajustando para o endpoint correto (`/webhook`):
    `https://api.telegram.org/bot<SEU_TOKEN>/setWebhook?url=https://abcd1234.ngrok.io/webhook`
   
  - Caso precise remover o webhook do Telegram:
    `https://api.telegram.org/bot<SEU_TOKEN>/deleteWebhook`

### 3. Configurar variáveis no `clima_script.py`

- Insira sua chave da OpenWeatherMap (`OWM_API_KEY`) `https://openweathermap.org/`
- Defina a cidade desejada (exemplo: `Blumenau,BR`)
- Configure o token do bot Telegram (`TELEGRAM_BOT_TOKEN`)
- Configure o chat ID (`TELEGRAM_CHAT_ID`) — nesse caso é obtido via webhook automaticamete
- Para consultar informações de ID do chat entre outras
  `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
  
---

### Executando localmente

Instale as dependências:

```bash
pip install -r requirements.txt
python webhook.py
ngrok http 5000
```

Entre no grupo e envie /clima no Telegram. O bot responderá com as informações do clima atual.

Estrutura dos arquivos
webhook.py — servidor Flask que recebe atualizações do Telegram e chama o script do clima.

clima_script.py — script que consulta a API de clima e envia mensagem ao Telegram e MQTT.

requirements.txt — lista de dependências Python.

Pode ser que você precise converter os arquivos para Unix com o comando:
```bash
dos2unix nomedoarquivo.py
```
Garanta que os arquivo estejam marcados como executáveis:
```
chmod +x nomedoarquivo.py
```
Pode precisar usar um Shebang no inicio dos scripts:
```bash
#!/usr/bin/env python
```
