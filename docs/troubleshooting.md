# 🐛 Troubleshooting - Solução de Problemas

## 🔴 Problemas Comuns

### ADK Web não inicia

#### Problema: `http://localhost:8000` não está funcionando

**Solução 1: Verificar se o servidor está rodando**
```bash
./scripts/start_adk_web.sh
```

**Solução 2: URL Correta**
- ✅ Interface principal: `http://localhost:8000`
- ✅ API Docs: `http://localhost:8000/docs`
- ❌ **NÃO** use `/dev-ui/` (não existe)

**Solução 3: Porta em uso**
```bash
# Verificar processos na porta 8000
lsof -i :8000
netstat -tulpn | grep 8000

# Parar processo ou alterar porta no script
```

**Solução 4: Verificar estrutura dos agentes**
```bash
# Verificar se há agentes no banco
curl http://localhost:8001/api/agents
```

---

### API REST não inicia

#### Problema: `http://localhost:8001` não está funcionando

**Solução 1: Verificar se está rodando**
```bash
./scripts/start_api.sh
```

**Solução 2: Verificar porta**
```bash
# Verificar processos na porta 8001
lsof -i :8001
```

**Solução 3: Verificar banco de dados**
```bash
docker-compose ps
# PostgreSQL deve estar "Running"
```

---

### Erro 429 (Resource Exhausted)

#### Problema: Limite de requisições da API Google Gemini

**Causas:**
- Muitas requisições em curto período
- Limite de quota atingido
- Múltiplas requisições simultâneas

**Soluções:**

1. **Aguardar e tentar novamente**
   - Erro 429 é temporário
   - Aguarde 1-2 minutos

2. **Verificar quotas**
   - Acesse: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

3. **Reduzir requisições**
   - Evite muitas requisições em sequência
   - Adicione delays durante testes

4. **Usar modelo diferente**
   - Tente `gemini-1.5-pro` ou `gemini-1.5-flash`

---

### Erro de conexão com banco de dados

#### Problema: PostgreSQL não conecta

**Solução 1: Verificar se está rodando**
```bash
docker-compose ps
```

**Solução 2: Iniciar serviços**
```bash
./scripts/start_services.sh
```

**Solução 3: Verificar variáveis de ambiente**
```bash
cat .env | grep DATABASE_URL
```

**Solução 4: Ver logs**
```bash
docker-compose logs postgres
```

---

### Erro de conexão com Redis

#### Problema: Redis não conecta

**Solução 1: Verificar se está rodando**
```bash
docker-compose ps
redis-cli -h localhost -p 6379 ping
# Deve retornar: PONG
```

**Solução 2: Iniciar serviços**
```bash
./scripts/start_services.sh
```

**Solução 3: Verificar variáveis de ambiente**
```bash
cat .env | grep REDIS
```

---

### Agentes não aparecem no ADK Web

#### Problema: Nenhum agente visível

**Solução 1: Verificar se há agentes no banco**
```bash
curl -H "Authorization: Bearer {token}" http://localhost:8001/api/agents
```

**Solução 2: Verificar se agentes estão ativos**
- Via API: Verifique `is_active = true`

**Solução 3: Verificar conexão com banco**
```bash
# Testar conexão
python -c "from src.database import test_connection; test_connection()"
```

**Solução 4: Recriar agente**
- Crie um novo agente via API REST

---

### Contexto não está sendo usado

#### Problema: Agente não lembra conversas anteriores

**Solução 1: Verificar se `session_id` está sendo passado**
```javascript
// Certifique-se de passar session_id
{
  "message": "Olá",
  "session_id": "sessao123"  // ⚠️ Importante!
}
```

**Solução 2: Verificar se Redis está funcionando**
```bash
redis-cli ping
```

**Solução 3: Verificar se sessão está associada**
```bash
POST /api/adk/sessions/{session_id}/associate
```

**Solução 4: Verificar logs**
- Verifique logs do servidor para erros

---

### Erro de autenticação

#### Problema: Token inválido ou expirado

**Solução 1: Fazer login novamente**
```bash
POST /api/auth/login
```

**Solução 2: Verificar formato do token**
```http
Authorization: Bearer {token}
```

**Solução 3: Verificar se token não expirou**
- Tokens JWT têm tempo de expiração
- Faça login novamente se necessário

---

### Erro de API Key

#### Problema: Google/OpenAI API Key inválida

**Solução 1: Verificar arquivo `.env`**
```bash
cat .env | grep API_KEY
```

**Solução 2: Verificar se keys estão corretas**
- Google: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys

**Solução 3: Recarregar variáveis**
```bash
# Reiniciar servidor após mudar .env
```

---

## 🔍 Verificação Rápida

Execute este script para verificar tudo:

```bash
#!/bin/bash
echo "=== Verificação do Sistema ==="

# Ambiente virtual
test -d .venv && echo "✓ Ambiente virtual OK" || echo "✗ Execute ./scripts/setup.sh"

# Serviços
docker-compose ps | grep -q "postgres.*Up" && echo "✓ PostgreSQL OK" || echo "✗ Execute ./scripts/start_services.sh"
docker-compose ps | grep -q "redis.*Up" && echo "✓ Redis OK" || echo "✗ Execute ./scripts/start_services.sh"

# Portas
lsof -i :8000 > /dev/null && echo "⚠ Porta 8000 em uso (ADK Web)" || echo "✓ Porta 8000 livre"
lsof -i :8001 > /dev/null && echo "⚠ Porta 8001 em uso (API)" || echo "✓ Porta 8001 livre"

# Arquivos
test -f .env && echo "✓ Arquivo .env existe" || echo "✗ Crie .env"
grep -q "GOOGLE_API_KEY" .env && echo "✓ Google API Key configurada" || echo "✗ Configure GOOGLE_API_KEY"

echo "=== Fim da Verificação ==="
```

---

## 📞 Obter Ajuda

1. **Consulte a documentação**: `docs/`
2. **Verifique logs**: `docker-compose logs`
3. **Verifique API Docs**: `http://localhost:8001/docs`
4. **Verifique variáveis de ambiente**: `.env`

---

## 📚 Documentação Relacionada

- [Guia de Início](getting-started.md)
- [Referência da API](api-reference.md)
- [Guia de Agentes](agent-guide.md)
- [Contexto Redis](redis-conversations.md)

