# Guia Rápido de Início

## Instalação Rápida

```bash
# 1. Execute o script de setup
./setup.sh

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env e adicione suas API keys

# 3. Inicie o PostgreSQL
docker-compose up -d

# 4. Execute a aplicação
python -m src.main
```

## Obter API Keys

### Google Gemini API Key
1. Acesse: https://makersuite.google.com/app/apikey
2. Crie uma nova API key
3. Adicione no arquivo `.env` como `GOOGLE_API_KEY`

### OpenAI API Key
1. Acesse: https://platform.openai.com/api-keys
2. Crie uma nova API key
3. Adicione no arquivo `.env` como `OPENAI_API_KEY`

## Testar os Agentes

### Interface Web do ADK (Recomendado)
```bash
./start_adk_web.sh
```
Acesse http://localhost:8000 no navegador

### Interface Web do ADK (Recomendado)
```bash
./start_adk_web.sh
```
Acesse http://localhost:8000 no navegador

### API REST (Gerenciamento de Agentes)
```bash
./start_api.sh
```
Acesse http://localhost:8001/docs para criar e gerenciar agentes

## Estrutura de Arquivos

```
agents-adk-google/
├── src/
│   ├── api/                 # API REST (FastAPI)
│   ├── adk_loader.py        # Carregador de agentes do banco
│   ├── adk_server.py        # Servidor ADK integrado
│   ├── config.py            # Configurações
│   ├── database.py          # Banco de dados
│   └── models.py            # Modelos (User, Agent)
├── tools/                   # Ferramentas compartilhadas
├── docker-compose.yml       # PostgreSQL
├── requirements.txt         # Dependências
├── start_adk_web.sh        # Interface Web ADK
├── start_api.sh            # API REST
└── .env                     # Variáveis de ambiente
```

## Troubleshooting

### Erro: "Missing required environment variables"
- Verifique se o arquivo `.env` existe e contém as API keys

### Erro: "Database connection error"
- Execute `docker-compose up -d` para iniciar o PostgreSQL
- Verifique se a porta 5432 está livre

### Erro: "ModuleNotFoundError: No module named 'google.adk'"
- Execute: `pip install google-adk`
- Verifique se o ambiente virtual está ativado

