# 🚀 Guia de Início Rápido

## Instalação Completa

### 1. Setup Inicial

```bash
./scripts/setup.sh
```

Este script:
- Verifica Python 3.9+
- Cria ambiente virtual
- Instala dependências
- Configura arquivo .env

### 2. Configurar API Keys

Edite o arquivo `.env` e adicione:

```env
GOOGLE_API_KEY=sua_chave_google_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
```

**Como obter:**

- **Google Gemini**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys

### 3. Iniciar Serviços

```bash
./scripts/start_services.sh
```

Isso inicia:
- PostgreSQL (porta 5432)
- Redis (porta 6379)

### 4. Inicializar Banco de Dados

```bash
./scripts/init_database.sh
```

Cria as tabelas necessárias.

## 🎯 Iniciar Aplicação

### Opção 1: API REST + ADK Web (Recomendado)

**Terminal 1 - API REST:**
```bash
./scripts/start_api.sh
```
- API: http://localhost:8001
- Docs: http://localhost:8001/docs

**Terminal 2 - ADK Web:**
```bash
./scripts/start_adk_web.sh
```
- Web UI: http://localhost:8000

### Opção 2: Apenas API REST

```bash
./scripts/start_api.sh
```

Use a API para chat: `POST /api/agents/chat`

## ✅ Verificação

### Verificar Serviços

```bash
docker-compose ps
```

Deve mostrar:
- `agents_postgres` - Running
- `agents_redis` - Running

### Testar API

```bash
curl http://localhost:8001/health
# Deve retornar: {"status":"healthy"}
```

### Testar ADK Web

Acesse: http://localhost:8000

## 📝 Próximos Passos

1. **Criar Usuário**: `POST /api/auth/register`
2. **Fazer Login**: `POST /api/auth/login`
3. **Criar Agente**: `POST /api/agents`
4. **Chat**: `POST /api/agents/chat`

Consulte a [Referência da API](api-reference.md) para detalhes completos.

