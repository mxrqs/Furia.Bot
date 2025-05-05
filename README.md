
# FURIA-BOT

FURIA-BOT é um projeto composto por um **bot do Telegram** (em Python) e um **backend Node.js** (API REST) que oferece suporte a funcionalidades auxiliares ao bot.

## 📁 Estrutura do Projeto

```
FURIA-BOT/
│
├── API/
│   └── backend/          # Backend em Node.js (rotas, serviços, etc.)
│       ├── routes/
│       ├── services/
│       ├── index.js
│       └── .env
│
├── bot/                  # Bot do Telegram (Python)
│   ├── Furia_bot.py
│   ├── .env.example
│   ├── requirements.txt
│   └── .env
│
├── .env                  # Ambiente geral (opcional)
├── package.json          # Dependências Node.js
├── requirements.txt      # Dependências Python
├── README.md             # Este arquivo
```

## 🚀 Como rodar o projeto

### 🔧 Pré-requisitos

- Node.js (v16+ recomendado)
- Python 3.9+
- pip
- `virtualenv` (opcional)
- Telegram bot token

### 1. Backend (Node.js)

```bash
cd API/backend
npm install
npm run dev
```

Ou, se estiver usando `nodemon`:
```bash
npx nodemon index.js
```

### 2. Bot do Telegram (Python)

```bash
cd bot
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
python Furia_bot.py
```

## 🔐 Variáveis de Ambiente

Crie arquivos `.env` nos diretórios `bot/` e `API/backend/`.

Exemplo para o **bot** (`bot/.env`):

```
BOT_TOKEN=seu_token_do_telegram
API_URL=http://localhost:3000
```

Exemplo para o **backend** (`API/backend/.env`):

```
PORT=3000
MONGO_URI=mongodb://localhost:27017/furia-db
```