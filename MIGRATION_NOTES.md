# Notas de Migração - Agentes do Banco de Dados

## ✅ Sistema Migrado

O sistema foi migrado para usar **exclusivamente** agentes do banco de dados PostgreSQL.

## 📋 O que Mudou

### Antes (Sistema Antigo)
- Agentes em arquivos Python na pasta `/agents`
- Cada agente em seu próprio diretório (`agents/calculator_agent/agent.py`)
- Necessário editar arquivos manualmente
- Não integrado com sistema de usuários

### Agora (Sistema Novo)
- ✅ Agentes armazenados no PostgreSQL
- ✅ Gerenciamento via API REST
- ✅ Cada usuário tem seus próprios agentes
- ✅ Sincronização automática com ADK
- ✅ Mais dinâmico e escalável

## 🚫 O que Não Funciona Mais

1. **Pasta `/agents`**: Não é mais usada para agentes ativos
2. **Scripts antigos**: 
   - `run_adk_interactive.sh` - Desabilitado
   - `start_adk_api.sh` - Desabilitado
3. **Edição manual**: Não edite arquivos em `/agents`

## ✅ O que Funciona Agora

1. **API REST**: `./start_api.sh` → `http://localhost:8001/docs`
   - Criar, editar, listar, deletar agentes
   - Sistema de usuários e autenticação

2. **Interface ADK**: `./start_adk_web.sh` → `http://localhost:8000`
   - Carrega automaticamente agentes do banco
   - Interface web para testar agentes

## 📝 Como Criar Agentes

### Via API REST (Recomendado)

```bash
# 1. Inicie a API
./start_api.sh

# 2. Acesse http://localhost:8001/docs

# 3. Faça login
POST /api/auth/login
{
  "email": "seu@email.com",
  "password": "senha"
}

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

### Exemplos Completos

Consulte `AGENT_CREATION_GUIDE.md` para exemplos detalhados de payloads.

## 🔄 Migrando Agentes Existentes

Se você tinha agentes na pasta `/agents` e quer migrá-los:

1. **Leia os agentes existentes** em `agents/calculator_agent/agent.py` e `agents/greeting_agent/agent.py`

2. **Crie via API REST** usando os dados dos agentes:
   - Nome
   - Descrição
   - Instruction
   - Model
   - Tools

3. **Exemplo de migração**:
   ```json
   {
     "name": "Calculator Agent",
     "description": "Realiza cálculos matemáticos",
     "instruction": "Você é um assistente especializado em cálculos...",
     "model": "gemini-2.0-flash-exp",
     "tools": ["calculator", "get_current_time"]
   }
   ```

## 📂 Estrutura de Arquivos

### Mantido (para referência)
- `/agents/` - Pasta mantida com README explicando que não é mais usada
- Arquivos antigos mantidos apenas para referência histórica

### Gerado Automaticamente
- `/.agents_db/` - Gerado automaticamente pelo sistema (não editar)
  - Este diretório é criado quando o servidor ADK inicia
  - Contém arquivos Python gerados a partir do banco de dados
  - É ignorado pelo git (`.gitignore`)

### Scripts Atualizados
- `start_adk_web.sh` - ✅ Usa agentes do banco
- `start_api.sh` - ✅ API REST para gerenciar agentes
- `run_adk_interactive.sh` - ⚠️ Desabilitado (mostra mensagem)
- `start_adk_api.sh` - ⚠️ Desabilitado (mostra mensagem)

## ✅ Checklist de Migração

- [x] Sistema carrega agentes do banco de dados
- [x] Scripts antigos desabilitados com mensagens claras
- [x] Documentação atualizada
- [x] `.gitignore` atualizado para ignorar `.agents_db/`
- [x] README na pasta `/agents` explicando mudança
- [ ] (Opcional) Migrar agentes existentes via API

## 🎯 Próximos Passos

1. **Criar seus agentes** via API REST em `http://localhost:8001/docs`
2. **Usar os agentes** na interface ADK em `http://localhost:8000`
3. **Não editar** arquivos em `/agents` ou `/.agents_db/`

## 📚 Documentação

- `AGENT_CREATION_GUIDE.md` - Guia completo para criar agentes
- `AGENTS_FROM_DB.md` - Como funciona o sistema de agentes do banco
- `API_DOCS.md` - Documentação completa da API REST

