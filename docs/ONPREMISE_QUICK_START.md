# Quick Start: Provedor On-Premise

Guia rápido para começar a usar o provedor LLM on-premise em 5 minutos.

## 🚀 Passo 1: Configurar Variáveis de Ambiente

Edite o arquivo `.env` e adicione:

```env
# URLs da API
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_CHAT_ENDPOINT=/api/chat
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token

# Credenciais OAuth
ONPREMISE_CONSUMER_KEY=sua_key_aqui
ONPREMISE_CONSUMER_SECRET=seu_secret_aqui
ONPREMISE_OAUTH_GRANT_TYPE=client_credentials

# SSL (false para dev, true para prod)
VERIFY_SSL=false
```

## ✅ Passo 2: Testar Configuração

Execute o script de teste:

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Executar teste
python scripts/test_onpremise_provider.py
```

O script irá:
- ✓ Verificar variáveis de ambiente
- ✓ Testar geração de token OAuth
- ✓ Validar conexão com a API
- ✓ Fazer uma requisição de teste

## 📝 Passo 3: Criar um Agente

### Via API REST

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente On-Premise",
    "description": "Assistente usando modelo on-premise",
    "model": "gpt-oss:20b",
    "instruction": "Você é um assistente útil que responde em português."
  }'
```

### Via Interface Web

1. Acesse http://localhost:8000
2. Clique em "New Agent"
3. Preencha:
   - **Name**: Assistente On-Premise
   - **Model**: `gpt-oss:20b` (ou outro modelo configurado)
   - **Instructions**: Suas instruções personalizadas
4. Clique em "Create"

## 💬 Passo 4: Conversar com o Agente

### Via API REST

```bash
curl -X POST http://localhost:8001/api/agents/AGENT_ID/chat \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá! Como você está?",
    "session_id": "session123"
  }'
```

### Via Interface Web

1. Selecione o agente criado
2. Digite sua mensagem no campo de chat
3. Pressione Enter ou clique em "Send"
4. Veja a resposta em tempo real (streaming)

## 🎛️ Passo 5: Personalizar Parâmetros (Opcional)

Ajuste os parâmetros do modelo conforme necessário:

```bash
curl -X POST http://localhost:8001/api/agents/AGENT_ID/chat \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explique inteligência artificial",
    "session_id": "session123",
    "temperature": 0.5,
    "num_predict": 2000,
    "top_p": 0.9,
    "num_ctx": 8192
  }'
```

### Parâmetros Disponíveis

| Parâmetro | Descrição | Padrão | Faixa |
|-----------|-----------|--------|-------|
| `temperature` | Criatividade da resposta | 0.1 | 0.0 - 1.0 |
| `top_p` | Nucleus sampling | 0.15 | 0.0 - 1.0 |
| `top_k` | Top-K sampling | 0 | 0+ |
| `num_predict` | Máximo de tokens | 500 | 1 - 4096 |
| `repeat_penalty` | Penalidade repetição | 1.1 | 0.0 - 2.0 |
| `num_ctx` | Tamanho do contexto | 4096 | 512 - 8192 |
| `seed` | Reprodutibilidade | - | Qualquer int |

## 🎯 Casos de Uso

### 1. Respostas Criativas

```json
{
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40
}
```

### 2. Respostas Precisas

```json
{
  "temperature": 0.1,
  "top_p": 0.15,
  "top_k": 0
}
```

### 3. Conversas Longas

```json
{
  "num_predict": 2000,
  "num_ctx": 8192
}
```

### 4. Respostas Determinísticas

```json
{
  "temperature": 0.0,
  "seed": 42
}
```

## 🔍 Verificar Status

### Verificar Modelos Disponíveis

```bash
curl -X GET http://localhost:8001/api/models \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Verificar Agentes

```bash
curl -X GET http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Verificar Configuração

```python
from src.config import Config
from src.core.llm_factory import LLMFactory

# Ver todos os modelos suportados
models = LLMFactory.get_all_supported_models()
print(models)

# Ver configuração on-premise
print(f"Base URL: {Config.ONPREMISE_API_BASE_URL}")
print(f"Models: {Config.ONPREMISE_MODELS}")
```

## ⚠️ Troubleshooting Rápido

### Problema: Token OAuth Falha
```bash
# Verificar credenciais
echo $ONPREMISE_CONSUMER_KEY
echo $ONPREMISE_CONSUMER_SECRET

# Testar manualmente
curl -X POST https://apidesenv.go.gov.br/token \
  -u "KEY:SECRET" \
  -d "grant_type=client_credentials"
```

### Problema: Timeout/Conexão
```bash
# Verificar conectividade
ping apidesenv.go.gov.br

# Testar endpoint
curl -v https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
```

### Problema: Certificado SSL
```env
# Adicionar no .env (apenas dev!)
VERIFY_SSL=false
```

### Problema: Modelo Não Reconhecido
```env
# Opção 1: Adicionar lista de modelos
ONPREMISE_MODELS=modelo1,modelo2,modelo3

# Opção 2: Usar formato com ":"
# Exemplo: gpt-oss:20b, llama-2:7b

# Opção 3: Usar prefixo
# Exemplo: local-modelo, onpremise-modelo
```

## 📚 Próximos Passos

1. **Documentação Completa**: Leia `docs/ONPREMISE_PROVIDER_SETUP.md`
2. **Exemplos**: Veja `docs/AGENT_ONPREMISE_EXAMPLE.json`
3. **API Reference**: Consulte `docs/API_DOCS.md`
4. **Integração com Tools**: Configure ferramentas MCP
5. **Monitoramento**: Configure logs e métricas

## 🎓 Dicas

✅ **Boas Práticas:**
- Use `temperature` baixa (0.1-0.3) para respostas consistentes
- Configure `num_ctx` maior para conversas longas
- Use `seed` para testes reproduzíveis
- Monitore o uso de tokens com `num_predict`

❌ **Evite:**
- `temperature` > 0.9 (respostas muito aleatórias)
- `num_predict` muito alto (lentidão)
- `VERIFY_SSL=false` em produção
- Credenciais expostas no código

## 🆘 Precisa de Ajuda?

- 📖 Documentação: `docs/ONPREMISE_PROVIDER_SETUP.md`
- 🐛 Issues: GitHub Issues
- 💬 Suporte: Equipe de desenvolvimento
- 🧪 Testes: `python scripts/test_onpremise_provider.py`

## ✨ Pronto!

Seu provedor on-premise está configurado e funcionando! 🎉

Agora você pode:
- ✅ Criar agentes com modelos on-premise
- ✅ Conversar via API ou interface web
- ✅ Personalizar parâmetros do modelo
- ✅ Integrar com ferramentas e RAG

