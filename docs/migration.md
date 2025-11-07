# 📝 Notas de Migração e Versões

## ✅ Sistema Atual

### Versão: 2.0 (Agentes do Banco de Dados)

O sistema foi migrado para usar **exclusivamente** agentes do banco de dados PostgreSQL.

---

## 📋 Mudanças Principais

### Antes (Sistema Antigo)
- Agentes em arquivos Python na pasta `/agents`
- Cada agente em seu próprio diretório
- Necessário editar arquivos manualmente
- Não integrado com sistema de usuários

### Agora (Sistema Novo)
- ✅ Agentes armazenados no PostgreSQL
- ✅ Gerenciamento via API REST
- ✅ Cada usuário tem seus próprios agentes
- ✅ Sincronização automática com ADK
- ✅ Contexto conversacional com Redis
- ✅ Chat via API REST

---

## 🚫 O que Não Funciona Mais

1. **Pasta `/agents`**: Não é mais usada para agentes ativos
2. **Scripts antigos**: 
   - `run_adk_interactive.sh` - Desabilitado
   - `start_adk_api.sh` - Desabilitado (agora usa `start_adk_web.sh` e `start_api.sh`)
3. **Edição manual**: Não edite arquivos em `/agents`

---

## ✅ Como Criar Agentes Agora

### Via API REST (Recomendado)

```bash
# 1. Inicie a API
./scripts/start_api.sh

# 2. Acesse http://localhost:8001/docs

# 3. Faça login
POST /api/auth/login

# 4. Crie um agente
POST /api/agents
{
  "name": "Meu Agente",
  "description": "Descrição",
  "instruction": "Você é um assistente...",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator"]
}
```

Consulte [Guia de Agentes](agent-guide.md) para exemplos completos.

---

## 🔄 Migrando Agentes Existentes

Se você tinha agentes na pasta `/agents`:

1. **Leia os agentes existentes** em `agents/*/agent.py`
2. **Extraia os dados**: nome, descrição, instruction, model, tools
3. **Crie via API REST** usando os dados extraídos

---

## 📂 Estrutura de Arquivos

### Mantido (para referência)
- `/agents/` - Pasta mantida com README explicando que não é mais usada

### Gerado Automaticamente
- `/.agents_db/` - Gerado quando ADK Web inicia (não editar)

### Scripts Atualizados
- `scripts/start_adk_web.sh` - ✅ Usa agentes do banco (porta 8000)
- `scripts/start_api.sh` - ✅ API REST (porta 8001)
- Scripts antigos desabilitados com mensagens claras

---

## 🎯 Novos Recursos

### Chat via API REST
- `POST /api/agents/chat` - Chat com agentes
- `POST /api/agents/{agent_id}/chat` - Chat com agente específico
- Suporte automático a contexto via Redis

### Contexto Conversacional
- Sistema de contexto com Redis
- Sessões conversacionais
- Histórico automático

### Frontend Customizado
- API REST completa para criar frontend próprio
- Não precisa do ADK Web para chat

---

## ✅ Checklist de Migração

- [x] Sistema carrega agentes do banco de dados
- [x] Scripts organizados em `scripts/`
- [x] Documentação consolidada em `docs/`
- [x] API e ADK Web em portas diferentes (8001 e 8000)
- [x] Sistema de contexto Redis implementado
- [x] Chat via API REST disponível

---

## 📚 Documentação

Toda documentação está em `docs/`:

- [Guia de Início](getting-started.md)
- [Referência da API](api-reference.md)
- [Guia de Agentes](agent-guide.md)
- [Contexto Redis](redis-conversations.md)
- [Frontend Customizado](frontend-guide.md)
- [Arquitetura](architecture.md)
- [Troubleshooting](troubleshooting.md)

---

## 🚀 Próximos Passos

1. **Criar agentes** via API REST
2. **Usar agentes** na interface ADK Web ou via API REST
3. **Implementar frontend** customizado usando a API REST
4. **Configurar contexto** conversacional com Redis

