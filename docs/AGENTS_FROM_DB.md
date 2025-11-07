# Agentes do Banco de Dados

## ✅ Sistema Implementado

O sistema agora carrega agentes **diretamente do banco de dados PostgreSQL** ao invés da pasta `/agents`.

## 🔄 Como Funciona

1. **Ao iniciar o servidor ADK** (`./start_adk_web.sh`):
   - O sistema conecta ao banco de dados
   - Carrega todos os agentes ativos da tabela `agents`
   - Gera dinamicamente arquivos Python no formato esperado pelo ADK
   - Inicia o servidor ADK com esses agentes

2. **Estrutura Gerada**:
   ```
   .agents_db/
     agents/
       db_agents/
         agent.py      # Gerado automaticamente
         __init__.py
   ```

3. **Sincronização Automática**:
   - Os agentes são sincronizados a cada inicialização do servidor
   - Mudanças no banco de dados são refletidas automaticamente
   - Não é necessário editar arquivos manualmente

## 📝 Criando Agentes

### Via API REST (Recomendado)

1. **Inicie a API REST:**
   ```bash
   ./start_api.sh
   ```

2. **Acesse a documentação:**
   ```
   http://localhost:8001/docs
   ```

3. **Faça login e crie agentes:**
   - POST `/api/auth/register` - Registrar usuário
   - POST `/api/auth/login` - Fazer login
   - POST `/api/agents` - Criar agente

### Exemplo de Payload

```json
{
  "name": "Calculadora",
  "description": "Agente especializado em cálculos matemáticos",
  "instruction": "Você é um assistente especializado em cálculos matemáticos. Quando receber uma expressão matemática, use a ferramenta calculator para calcular o resultado. Apresente o resultado de forma clara e use português brasileiro.",
  "model": "gemini-2.0-flash-exp",
  "tools": ["calculator"]
}
```

## 🚀 Usando os Agentes

### Iniciar Interface Web ADK

```bash
./start_adk_web.sh
```

A interface estará disponível em:
- **Interface Web**: http://localhost:8000

### Agentes Disponíveis

Todos os agentes ativos do banco de dados estarão disponíveis na interface web do ADK.

## 🔧 Estrutura Técnica

### Arquivos Principais

- `src/adk_loader.py` - Carrega agentes do banco e gera estrutura ADK
- `src/adk_server.py` - Servidor que integra ADK com banco de dados
- `start_adk_web.sh` - Script atualizado para usar agentes do banco

### Fluxo de Dados

```
Banco de Dados (PostgreSQL)
    ↓
src/adk_loader.py (carrega agentes)
    ↓
.agents_db/agents/db_agents/agent.py (gerado dinamicamente)
    ↓
ADK Web Server (adk web)
    ↓
Interface Web (http://localhost:8000)
```

## ⚙️ Configuração

### Tools Disponíveis

As seguintes tools podem ser usadas nos agentes:

- `"calculator"` - Calculadora matemática
- `"get_current_time"` - Informações de data/hora

### Modelos Disponíveis

- `"gemini-2.0-flash-exp"` (padrão)
- `"gemini-1.5-pro"`
- `"gemini-1.5-flash"`

## 📋 Diferenças do Sistema Anterior

### Antes (Pasta `/agents`)
- Agentes em arquivos Python na pasta `/agents`
- Cada agente em seu próprio diretório
- Necessário editar arquivos manualmente
- Não integrado com sistema de usuários

### Agora (Banco de Dados)
- Agentes armazenados no PostgreSQL
- Gerenciamento via API REST
- Cada usuário tem seus próprios agentes
- Sincronização automática com ADK
- Mais dinâmico e escalável

## 🐛 Troubleshooting

### Nenhum agente aparece

1. Verifique se há agentes no banco:
   ```bash
   # Via API
   GET http://localhost:8001/api/agents
   ```

2. Verifique se os agentes estão ativos (`is_active = true`)

3. Verifique a conexão com o banco de dados

### Erro ao sincronizar

1. Verifique se o PostgreSQL está rodando:
   ```bash
   docker-compose up -d
   ```

2. Verifique as variáveis de ambiente no `.env`

3. Verifique os logs do servidor

## 📚 Arquivos Relacionados

- `AGENT_CREATION_GUIDE.md` - Guia completo para criar agentes
- `API_DOCS.md` - Documentação da API REST
- `TROUBLESHOOTING_ADK.md` - Solução de problemas do ADK

