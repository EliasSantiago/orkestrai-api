# Troubleshooting - ADK Dev-UI

## Problema: `http://localhost:8000/dev-ui/` não está funcionando

### ✅ Solução 1: Verificar se o servidor ADK está rodando

O servidor ADK precisa estar ativo. Execute:

```bash
./start_adk_web.sh
```

Você deve ver a mensagem:
```
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://0.0.0.0:8000.                         |
+-----------------------------------------------------------------------------+
```

### ✅ Solução 2: URL Correta

O ADK Web Server está disponível na **raiz**, não em `/dev-ui/`:

**URLs corretas:**
- **Interface principal**: `http://localhost:8000`
- **API Docs (Swagger)**: `http://localhost:8000/docs`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

**❌ URL incorreta:**
- `http://localhost:8000/dev-ui/` (não existe)

### ✅ Solução 3: Verificar se a porta 8000 está livre

Se a porta 8000 estiver em uso, você verá um erro. Verifique:

```bash
# Verificar processos na porta 8000
lsof -i :8000

# Ou
netstat -tulpn | grep 8000
```

Se algo estiver usando a porta, você pode:
1. Parar o processo que está usando a porta
2. Ou alterar a porta no script `start_adk_web.sh`:
   ```bash
   adk web agents --host=0.0.0.0 --port=8001
   ```

### ✅ Solução 4: Verificar estrutura dos agentes

O ADK requer que cada agente tenha um `root_agent` definido. Verifique:

```bash
# Verificar se os agentes existem
ls -la agents/*/agent.py

# Verificar se cada agent.py tem root_agent
grep -r "root_agent" agents/*/agent.py
```

### ✅ Solução 5: Iniciar o servidor corretamente

**Passo a passo:**

1. **Certifique-se de que o ambiente virtual está ativo:**
   ```bash
   source .venv/bin/activate
   ```

2. **Inicie o servidor ADK:**
   ```bash
   ./start_adk_web.sh
   ```

3. **Acesse no navegador:**
   - Abra: `http://localhost:8000`
   - **NÃO** use `/dev-ui/`

### ✅ Solução 6: Verificar variáveis de ambiente

Certifique-se de que o arquivo `.env` existe e contém:

```bash
GOOGLE_API_KEY=your_api_key_here
```

Sem a API key, o servidor pode iniciar mas os agentes não funcionarão.

### 🔍 Verificação Rápida

Execute este comando para verificar tudo:

```bash
# 1. Verificar se o ambiente virtual existe
test -d .venv && echo "✓ Ambiente virtual OK" || echo "✗ Execute ./setup.sh"

# 2. Verificar se os agentes existem
test -d agents && echo "✓ Diretório agents OK" || echo "✗ Diretório agents não encontrado"

# 3. Verificar se os agentes têm root_agent
grep -q "root_agent" agents/*/agent.py && echo "✓ root_agent encontrado" || echo "✗ root_agent não encontrado"

# 4. Verificar se a porta está livre
lsof -i :8000 > /dev/null && echo "⚠ Porta 8000 em uso" || echo "✓ Porta 8000 livre"

# 5. Verificar se .env existe
test -f .env && echo "✓ Arquivo .env existe" || echo "✗ Arquivo .env não encontrado"
```

### 📝 Exemplo de Uso Correto

```bash
# Terminal 1: Iniciar servidor ADK
./start_adk_web.sh

# Terminal 2: Verificar se está rodando
curl http://localhost:8000/docs

# Navegador: Acessar
# http://localhost:8000
```

### ❌ Erros Comuns

1. **"Connection refused"**
   - O servidor não está rodando
   - Execute `./start_adk_web.sh`

2. **"Port already in use"**
   - Outro processo está usando a porta 8000
   - Pare o processo ou mude a porta

3. **"No root_agent found"**
   - O arquivo `agent.py` não tem `root_agent`
   - Verifique se cada agente tem `root_agent = Agent(...)`

4. **"404 Not Found" em `/dev-ui/`**
   - A URL correta é `http://localhost:8000` (sem `/dev-ui/`)
   - O ADK não usa `/dev-ui/` como endpoint

### 🔗 URLs Importantes

- **Interface Web ADK**: `http://localhost:8000`
- **Documentação Swagger**: `http://localhost:8000/docs`
- **API REST (FastAPI)**: `http://localhost:8001` (servidor diferente)
- **API Docs (FastAPI)**: `http://localhost:8001/docs`

**Nota:** O servidor ADK (`./start_adk_web.sh`) roda na porta **8000**.
O servidor FastAPI (`./start_api.sh`) roda na porta **8001**.

São servidores diferentes com propósitos diferentes!

