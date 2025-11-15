# 🐳 LobeChat com Docker - Conectar à sua API

## ✅ Solução para o Erro ECONNREFUSED

Quando o LobeChat está no Docker, ele **não pode** acessar `localhost:8001` porque `localhost` dentro do container refere-se ao próprio container, não ao host.

---

## 🚀 Solução Rápida

### Passo 1: Use o docker-compose.yml pronto

Já criei um arquivo pronto para você: `docker-compose.lobechat.yml`

```bash
# Na raiz do projeto
docker-compose -f docker-compose.lobechat.yml up -d
```

Acesse: `http://localhost:3210`

### Passo 2: Configure no LobeChat

No LobeChat, vá em **Configurações** e configure:

```
Base URL: http://host.docker.internal:8001/v1
API Key: your-api-key-here
```

---

## 📝 Configuração Detalhada

### Se você já tem um docker-compose.yml do LobeChat

Adicione/modifique estas linhas:

```yaml
services:
  lobechat:
    environment:
      # Mude de localhost para host.docker.internal
      API_BASE_URL: "http://host.docker.internal:8001/v1"
      OPENAI_API_KEY: "your-api-key-here"
    
    # Adicione esta seção
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

Depois reinicie:

```bash
docker-compose down
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Problema: `host.docker.internal` não funciona

**Solução 1: Use o IP da sua máquina**

```bash
# Descobrir seu IP
hostname -I | awk '{print $1}'
```

Depois use no LobeChat:

```
Base URL: http://SEU_IP:8001/v1
API Key: your-api-key-here
```

Por exemplo:
```
Base URL: http://192.168.1.100:8001/v1
```

**Solução 2: Use network_mode: host (Linux apenas)**

```yaml
services:
  lobechat:
    network_mode: host
    environment:
      API_BASE_URL: "http://localhost:8001/v1"
```

**⚠️ Nota:** Isso só funciona no Linux.

---

## 🧪 Testar Conexão

### Teste 1: Verificar se API está acessível do container

```bash
# Entrar no container do LobeChat
docker exec -it lobechat sh

# Tentar acessar a API (dentro do container)
wget -qO- http://host.docker.internal:8001/health

# Deve retornar: {"status":"healthy"}
```

### Teste 2: Ver logs do LobeChat

```bash
docker logs lobechat -f
```

Procure por erros de conexão.

### Teste 3: Testar da sua máquina

```bash
# Da sua máquina (fora do Docker)
curl http://localhost:8001/v1/models \
  -H "Authorization: Bearer test"
```

Deve listar os modelos disponíveis.

---

## 📊 Arquitetura

```
┌─────────────────────────────┐
│   Docker Container          │
│                             │
│   ┌──────────────────────┐  │
│   │                      │  │
│   │    LobeChat          │  │
│   │  (localhost:3210)    │  │
│   │                      │  │
│   └──────────┬───────────┘  │
│              │              │
└──────────────┼──────────────┘
               │
               │ http://host.docker.internal:8001/v1
               │
               ▼
┌──────────────────────────────┐
│   Host Machine               │
│                              │
│   ┌──────────────────────┐   │
│   │                      │   │
│   │  Sua API FastAPI     │   │
│   │  (localhost:8001)    │   │
│   │                      │   │
│   └──────────────────────┘   │
│                              │
└──────────────────────────────┘
```

---

## 🎯 Checklist

- [ ] API está rodando (`curl http://localhost:8001/health`)
- [ ] LobeChat está rodando (`docker ps | grep lobechat`)
- [ ] Configurou `host.docker.internal:8001/v1` no LobeChat
- [ ] Adicionou `extra_hosts` no docker-compose.yml
- [ ] Reiniciou o container (`docker-compose restart`)
- [ ] Testou enviando uma mensagem no LobeChat
- [ ] Funciona! 🎉

---

## 🔥 Comandos Úteis

```bash
# Iniciar LobeChat
docker-compose -f docker-compose.lobechat.yml up -d

# Ver logs
docker logs lobechat -f

# Reiniciar
docker-compose -f docker-compose.lobechat.yml restart

# Parar
docker-compose -f docker-compose.lobechat.yml down

# Ver status
docker ps | grep lobechat

# Entrar no container
docker exec -it lobechat sh
```

---

## 📚 Arquivos Criados

- `docker-compose.lobechat.yml` - Docker Compose pronto para usar
- `LOBECHAT_DOCKER_SETUP.md` - Este guia
- `LOBECHAT_QUICKSTART.md` - Quick start geral
- `docs/LOBECHAT_INTEGRATION.md` - Documentação completa

---

## 💡 Dicas

### Persistir Conversas

Para não perder conversas ao reiniciar:

```yaml
services:
  lobechat:
    volumes:
      - ./lobechat-data:/app/data
```

### Usar com Banco de Dados

Descomente a seção `postgres` no `docker-compose.lobechat.yml` e:

```yaml
services:
  lobechat:
    environment:
      DATABASE_URL: "postgresql://lobechat:lobechat@postgres:5432/lobechat"
```

### Configurar Código de Acesso

```yaml
services:
  lobechat:
    environment:
      ACCESS_CODE: "meu-codigo-secreto-123"
```

---

## ✅ Resumo da Solução

**Problema:** LobeChat no Docker não pode acessar `localhost:8001`

**Solução:** Usar `host.docker.internal:8001` em vez de `localhost:8001`

**Como:** 
1. No docker-compose.yml: `API_BASE_URL: "http://host.docker.internal:8001/v1"`
2. Adicionar: `extra_hosts: - "host.docker.internal:host-gateway"`
3. Reiniciar: `docker-compose restart`

**Teste:** Enviar mensagem no LobeChat e deve funcionar! 🎉

---

**Última atualização:** 2025-11-12

