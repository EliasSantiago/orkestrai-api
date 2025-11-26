# 🔧 Guia para Executar Migrations Manualmente no Servidor

## Opção 1: Esperar o Próximo Deploy (RECOMENDADO) ✅

As migrations agora serão executadas **automaticamente** quando o container for reiniciado no próximo deploy.

**O que foi feito:**
- ✅ `docker-entrypoint.sh` atualizado para executar migrations automaticamente
- ✅ Script `run_token_migrations.sh` criado para executar migrations do sistema de tokens
- ✅ Migrations são idempotentes (podem rodar múltiplas vezes com segurança)
- ✅ Todas as mudanças commitadas e enviadas para o repositório

**No próximo deploy, o container irá:**
1. Iniciar
2. Executar `migrate_database.sh` (migrations SQL)
3. Executar `run_token_migrations.sh` (migrations Python do sistema de tokens)
4. Iniciar o servidor API

---

## Opção 2: Executar Manualmente Agora

Se você quiser executar as migrations antes do próximo deploy, siga estes passos:

### Passo 1: Conectar ao Servidor

```bash
# Use sua chave SSH ou método de acesso habitual
ssh SEU_USUARIO@34.42.168.19
```

### Passo 2: Encontrar o Container da API

```bash
# Listar containers
docker ps

# Procurar por 'orkestrai-api' ou 'api'
```

### Passo 3: Executar Migrations no Container

```bash
# Substitua CONTAINER_NAME pelo nome real do container
CONTAINER_NAME="orkestrai-api"

# Executar migrations SQL
docker exec $CONTAINER_NAME bash /app/scripts/migrate_database.sh

# Executar migrations Python (sistema de tokens)
docker exec $CONTAINER_NAME bash /app/scripts/run_token_migrations.sh
```

### Passo 4: Verificar se as Migrations Foram Aplicadas

```bash
# Conectar ao PostgreSQL
docker exec agents_postgres psql -U agentuser -d agentsdb

# Verificar planos (deve mostrar free com 2000 tokens)
SELECT id, name, monthly_token_limit FROM plans;

# Verificar migrations aplicadas
SELECT * FROM python_migrations;

# Sair
\q
```

---

## 🎯 O que as Migrations Fazem

### 1. Sistema de Tokens (`create_token_system_tables`)
- Cria tabela `plans` (free, pro, plus)
- Atualiza plano free para **2.000 tokens**
- Cria tabela `user_token_balances`
- Cria tabela `token_usage_history`
- Adiciona coluna `plan_id` na tabela `users`
- Atribui todos os usuários ao plano free

### 2. Trigger Automático (`add_auto_assign_free_plan_trigger`)
- Cria trigger para atribuir plano free automaticamente a novos usuários
- Garante que todo novo usuário receba 2.000 tokens

---

## 🔍 Verificar Status das Migrations

### No Container:
```bash
docker exec orkestrai-api bash -c "cd /app && python3 -c \"
from src.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Verificar migrations Python
    result = conn.execute(text('SELECT * FROM python_migrations'))
    print('\\nMigrations Python aplicadas:')
    for row in result:
        print(f'  - {row.migration_name}: {\"✓\" if row.success else \"✗\"} ({row.applied_at})')
    
    # Verificar planos
    result = conn.execute(text('SELECT name, monthly_token_limit FROM plans'))
    print('\\nPlanos configurados:')
    for row in result:
        print(f'  - {row.name}: {row.monthly_token_limit:,} tokens')
\""
```

### No PostgreSQL:
```bash
docker exec agents_postgres psql -U agentuser -d agentsdb -c "
SELECT 
    p.name as plano,
    p.monthly_token_limit as limite,
    COUNT(u.id) as usuarios
FROM plans p
LEFT JOIN users u ON u.plan_id = p.id
GROUP BY p.id, p.name, p.monthly_token_limit
ORDER BY p.id;
"
```

---

## ⚠️ Notas Importantes

1. **Idempotência**: As migrations podem ser executadas múltiplas vezes com segurança
2. **Tabela de Controle**: `python_migrations` rastreia quais migrations já foram aplicadas
3. **Sem Interrupção**: As migrations rodam antes do servidor iniciar (sem downtime)
4. **Rollback**: Não há rollback automático - as migrations são projetadas para serem seguras

---

## 📝 Logs

Para ver os logs das migrations durante o startup do container:

```bash
# Ver logs em tempo real
docker logs -f orkestrai-api

# Ver últimas 100 linhas
docker logs --tail 100 orkestrai-api | grep -E "Migration|migration|Token|tokens"
```

---

## ✅ Commits Realizados

1. **77c364fc**: Update free plan token limit from 200k to 2k tokens
2. **9e463ce5**: Add database trigger to auto-assign free plan to new users
3. **126241a3**: Add automatic migrations on container startup

Todas as mudanças estão no repositório e serão aplicadas no próximo deploy! 🚀

