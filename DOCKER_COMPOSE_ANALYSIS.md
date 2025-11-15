# 📊 Análise Detalhada do docker-compose.yml

## 🔄 Resumo das Alterações

Este documento explica todas as mudanças feitas no `docker-compose.yml` para prepará-lo para produção, com foco em segurança, performance e gerenciamento de recursos.

---

## 🔐 1. SEGURANÇA - Variáveis de Ambiente

### Antes:
```yaml
environment:
  POSTGRES_USER: agentuser
  POSTGRES_PASSWORD: agentpass
```

### Depois:
```yaml
environment:
  POSTGRES_USER: ${POSTGRES_USER:-agentuser}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  POSTGRES_DB: ${POSTGRES_DB:-agentsdb}
```

### O que mudou:
- ✅ **Senhas movidas para arquivo `.env`** - Nunca mais hardcoded no código
- ✅ **Valores padrão** usando `${VAR:-default}` - Se a variável não existir, usa o padrão
- ✅ **POSTGRES_PASSWORD sem padrão** - Força o uso de senha segura do `.env`
- ✅ **POSTGRES_HOST_AUTH_METHOD: scram-sha-256** - Método de autenticação mais seguro

### Por que é importante:
- Senhas no código são um risco de segurança crítico
- Arquivo `.env` pode ser ignorado pelo Git (não vai para repositório)
- Facilita diferentes configurações por ambiente (dev/staging/prod)

---

## 🔒 2. SEGURANÇA - Redis com Senha

### Antes:
```yaml
command: redis-server --appendonly yes
```

### Depois:
```yaml
command: >
  redis-server
  --appendonly yes
  --requirepass ${REDIS_PASSWORD}
  --maxmemory 512mb
  --maxmemory-policy allkeys-lru
```

### O que mudou:
- ✅ **`--requirepass`** - Redis agora exige senha para conexão
- ✅ **`--maxmemory 512mb`** - Limita uso de memória do Redis
- ✅ **`--maxmemory-policy allkeys-lru`** - Remove chaves menos usadas quando memória cheia
- ✅ **Healthcheck atualizado** - Agora usa senha: `redis-cli -a ${REDIS_PASSWORD} ping`

### Por que é importante:
- Redis sem senha é um risco de segurança (qualquer um pode acessar)
- Previne uso excessivo de memória
- Evita que Redis trave o servidor por falta de memória

---

## 🌐 3. REDE - Network Isolada

### Antes:
```yaml
# Sem network definida - containers na network padrão
```

### Depois:
```yaml
networks:
  agents_network:
    driver: bridge
    name: agents_network

services:
  postgres:
    networks:
      - agents_network
  redis:
    networks:
      - agents_network
```

### O que mudou:
- ✅ **Network dedicada** - Containers isolados em sua própria rede
- ✅ **Comunicação interna** - Containers se comunicam pelo nome do serviço
- ✅ **Melhor organização** - Facilita gerenciamento e troubleshooting

### Por que é importante:
- Isolamento de rede aumenta segurança
- Facilita adicionar mais serviços no futuro
- Containers se comunicam por nome (`postgres`, `redis`) ao invés de IP

---

## 💾 4. VOLUMES - Nomes Explícitos

### Antes:
```yaml
volumes:
  pg_data:
  redis_data:
```

### Depois:
```yaml
volumes:
  pg_data:
    name: agents_pg_data
  redis_data:
    name: agents_redis_data
```

### O que mudou:
- ✅ **Nomes explícitos** - Facilita identificação em `docker volume ls`
- ✅ **Backup mais fácil** - Nome claro para scripts de backup

### Por que é importante:
- Evita confusão com volumes de outros projetos
- Facilita backup e restauração
- Melhor organização

---

## 🏥 5. HEALTHCHECKS - Monitoramento Melhorado

### Antes:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U agentuser -d agentsdb"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Depois:
```yaml
# PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB} || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s  # ⬅️ NOVO

# Redis
healthcheck:
  test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
  start_period: 10s  # ⬅️ NOVO
```

### O que mudou:
- ✅ **`start_period`** - Período de graça durante inicialização (evita falhas prematuras)
- ✅ **Healthcheck do Redis com senha** - Funciona com autenticação
- ✅ **Variáveis dinâmicas** - Usa variáveis de ambiente

### Por que é importante:
- Docker sabe quando container está realmente pronto
- Evita tentativas de conexão durante inicialização
- Facilita orquestração e auto-restart

---

## 📝 6. LOGGING - Rotação de Logs

### Antes:
```yaml
# Sem configuração de logging
```

### Depois:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"    # Cada arquivo de log máximo 10MB
    max-file: "3"      # Manter apenas 3 arquivos (30MB total)
```

### O que mudou:
- ✅ **Rotação automática** - Logs não crescem infinitamente
- ✅ **Limite de espaço** - Máximo 30MB por container (3 arquivos × 10MB)
- ✅ **Formato JSON** - Facilita parsing por ferramentas de log

### Por que é importante:
- Previne que logs consumam todo o disco
- Facilita análise de logs
- Melhor para produção

---

## ⚙️ 7. LIMITES DE RECURSOS (Resource Limits)

### O que são limites de recursos?

Limites de recursos controlam quanto CPU e memória cada container pode usar. Isso previne que um container "engula" todos os recursos do servidor.

### Estrutura:

```yaml
deploy:
  resources:
    limits:        # Máximo que o container PODE usar
      cpus: '2.0'   # Máximo 2 CPUs completos
      memory: 2G   # Máximo 2GB de RAM
    reservations:  # Mínimo GARANTIDO ao container
      cpus: '0.5'  # Garante pelo menos 0.5 CPU
      memory: 512M # Garante pelo menos 512MB de RAM
```

### PostgreSQL - Configuração Atual:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Máximo: 2 CPUs completos
      memory: 2G        # Máximo: 2GB RAM
    reservations:
      cpus: '0.5'       # Garantido: 0.5 CPU (50% de 1 core)
      memory: 512M      # Garantido: 512MB RAM
```

**Interpretação:**
- PostgreSQL **pode usar até** 2 CPUs e 2GB RAM quando necessário
- PostgreSQL **tem garantido** pelo menos 0.5 CPU e 512MB RAM sempre
- Se o servidor tiver poucos recursos, outros containers não podem "roubar" os 512MB garantidos

### Redis - Configuração Atual:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'       # Máximo: 1 CPU completo
      memory: 1G         # Máximo: 1GB RAM
    reservations:
      cpus: '0.25'       # Garantido: 0.25 CPU (25% de 1 core)
      memory: 256M       # Garantido: 256MB RAM
```

**Interpretação:**
- Redis **pode usar até** 1 CPU e 1GB RAM quando necessário
- Redis **tem garantido** pelo menos 0.25 CPU e 256MB RAM sempre
- Note que o Redis já tem `--maxmemory 512mb` configurado, então o limite de 1GB é um "teto extra"

### Por que usar limites?

#### ✅ Vantagens:

1. **Previne "Noisy Neighbor"**
   - Um container não pode consumir todos os recursos
   - Outros containers/serviços continuam funcionando

2. **Previsibilidade**
   - Você sabe quanto cada serviço vai usar
   - Facilita planejamento de capacidade

3. **Estabilidade**
   - Evita que servidor trave por falta de memória
   - Sistema operacional não precisa fazer "OOM Kill" (matar processos)

4. **Custos**
   - Em cloud, ajuda a dimensionar instâncias corretamente
   - Evita surpresas na conta

#### ⚠️ Considerações:

1. **Ajuste conforme necessidade**
   - Valores atuais são **estimativas**
   - Monitore uso real e ajuste:
     ```bash
     docker stats agents_postgres agents_redis
     ```

2. **Reservations vs Limits**
   - **Reservations**: Recursos garantidos (podem não estar disponíveis se servidor estiver cheio)
   - **Limits**: Máximo absoluto (container nunca passa disso)

3. **CPU em Docker Compose**
   - `cpus: '2.0'` = 2 CPUs completos
   - `cpus: '0.5'` = 50% de 1 CPU
   - Valores podem ser decimais

4. **Memória**
   - Valores em MB, GB, etc.
   - `2G` = 2 gigabytes
   - `512M` = 512 megabytes

### Como monitorar uso real:

```bash
# Ver uso atual de recursos
docker stats agents_postgres agents_redis

# Ver uso detalhado
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Recomendações de Ajuste:

**Para servidor pequeno (2GB RAM, 2 CPUs):**
```yaml
# PostgreSQL
limits:
  cpus: '1.0'
  memory: 1G
reservations:
  cpus: '0.25'
  memory: 256M

# Redis
limits:
  cpus: '0.5'
  memory: 512M
reservations:
  cpus: '0.1'
  memory: 128M
```

**Para servidor médio (4GB RAM, 4 CPUs):**
```yaml
# Valores atuais estão bons
```

**Para servidor grande (8GB+ RAM, 8+ CPUs):**
```yaml
# PostgreSQL
limits:
  cpus: '4.0'
  memory: 4G
reservations:
  cpus: '1.0'
  memory: 1G

# Redis
limits:
  cpus: '2.0'
  memory: 2G
reservations:
  cpus: '0.5'
  memory: 512M
```

---

## 🔧 8. PORTAS - Variáveis de Ambiente

### Antes:
```yaml
ports:
  - "5432:5432"
  - "6379:6379"
```

### Depois:
```yaml
ports:
  - "${POSTGRES_PORT:-5432}:5432"
  - "${REDIS_PORT:-6379}:6379"
```

### O que mudou:
- ✅ **Portas configuráveis** - Pode mudar porta do host via `.env`
- ✅ **Valores padrão** - Se não definir, usa 5432 e 6379

### Por que é importante:
- Facilita rodar múltiplas instâncias
- Evita conflitos de porta
- Útil para desenvolvimento local

---

## 📊 Resumo Comparativo

| Aspecto | Antes | Depois | Impacto |
|---------|-------|--------|---------|
| **Senhas** | Hardcoded | Arquivo `.env` | 🔒 Alta segurança |
| **Redis Auth** | Sem senha | Com senha obrigatória | 🔒 Alta segurança |
| **Network** | Padrão | Isolada | 🔒 Segurança média |
| **Limites** | Sem limites | CPU + Memória | ⚡ Performance + Estabilidade |
| **Logging** | Sem rotação | Rotação automática | 📝 Manutenção |
| **Healthcheck** | Básico | Melhorado | 🏥 Confiabilidade |
| **Portas** | Fixas | Configuráveis | 🔧 Flexibilidade |

---

## 🎯 Próximos Passos Recomendados

1. **Monitorar uso real de recursos:**
   ```bash
   docker stats agents_postgres agents_redis
   ```
   Ajustar limites conforme necessário.

2. **Considerar remover exposição de portas:**
   Se aplicação Python estiver na mesma máquina, pode acessar via network interna:
   ```yaml
   # Remover ports: e acessar via network
   # postgres://agentuser:senha@postgres:5432/agentsdb
   ```

3. **Configurar backups:**
   - Volume `agents_pg_data` precisa de backup regular
   - Volume `agents_redis_data` (opcional, depende do uso)

4. **Revisar limites periodicamente:**
   - Ajustar conforme carga real
   - Monitorar métricas de uso

---

## 📚 Referências

- [Docker Compose Resource Limits](https://docs.docker.com/compose/compose-file/compose-file-v3/#deploy)
- [PostgreSQL Resource Tuning](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [Redis Memory Management](https://redis.io/docs/management/memory/)

