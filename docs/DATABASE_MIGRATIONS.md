# 🗄️ Migrações de Banco de Dados - Modo Seguro

Sistema de criação e migração de tabelas com abordagem conservadora para produção.

## 🔒 Filosofia de Segurança

### ✅ **Automático (Seguro):**
- Criar tabelas **apenas na primeira vez** (se banco vazio)
- Verificação antes de criar (não sobrescreve)
- Idempotente (pode rodar múltiplas vezes)

### 🔧 **Manual (Produção):**
- Migrations SQL são **sempre manuais**
- Você tem controle total
- Backup obrigatório antes
- Múltiplas confirmações

## 🎯 Como Funciona

### Primeira Vez (Automático):

```
1. Deploy rodando pela primeira vez
   ↓
2. Verifica: banco tem tabelas?
   ├─ SIM → Pula (não faz nada) ✅
   └─ NÃO → Cria tabelas via SQLAlchemy ✅
   ↓
3. Inicia aplicação
```

### Deploys Subsequentes:

```
1. Deploy rodando
   ↓
2. Verifica: banco tem tabelas?
   ├─ SIM → Pula criação ✅ (seguro!)
   └─ Inicia aplicação
```

### Migrations SQL (Manual):

```
1. Você decide quando aplicar
   ↓
2. Faz backup primeiro
   ↓
3. Executa script com múltiplas confirmações
   ↓
4. Registra migration aplicada
```

## 📋 Tabelas Criadas Automaticamente (Primeira Vez)

- **`users`** - Usuários do sistema
- **`agents`** - Agentes de IA
- **`password_reset_tokens`** - Tokens de reset
- **`mcp_connections`** - Conexões MCP
- **`file_search_stores`** - Busca de arquivos
- **`file_search_files`** - Arquivos indexados
- **`conversation_sessions`** - Sessões de conversa
- **`conversation_messages`** - Mensagens
- **`schema_migrations`** - Controle de migrations (criada quando necessário)

## 🛠️ Aplicar Migration SQL Manual

### Passo a Passo Seguro:

```bash
# 1. FAZER BACKUP PRIMEIRO!
./scripts/backup_db.sh

# 2. Revisar a migration SQL
cat migrations/add_new_column.sql

# 3. Aplicar com script seguro
./scripts/apply_migration.sh migrations/add_new_column.sql
```

### O que o script faz:

1. ✅ Mostra conteúdo do SQL para você revisar
2. ✅ Pede confirmação 1: "Você revisou?"
3. ✅ Verifica se já foi aplicada
4. ✅ Oferece fazer backup
5. ✅ Pede confirmação 2: "Fazer backup?"
6. ✅ Pede confirmação 3: Digite "APLICAR"
7. ✅ Aplica a migration
8. ✅ Registra em `schema_migrations`
9. ✅ Mostra resultado

### Exemplo Prático:

```bash
$ ./scripts/apply_migration.sh migrations/add_user_phone.sql

⚠️  Aplicar Migration SQL - MODO MANUAL
========================================

⚠️  ATENÇÃO - AMBIENTE DE PRODUÇÃO

Migration: add_user_phone.sql

Esta operação pode modificar dados em produção!

Conteúdo da migration:
----------------------------------------
ALTER TABLE users 
ADD COLUMN phone VARCHAR(20);

CREATE INDEX idx_users_phone ON users(phone);
----------------------------------------

Você revisou o SQL acima? (sim/não): sim

Verificando se já foi aplicada...
✓ Migration não foi aplicada

📦 RECOMENDADO: Fazer backup antes
Deseja fazer backup do banco agora? (sim/não): sim

Fazendo backup...
✓ Backup criado: backups/backup_20250115.sql.gz

⚠️  ÚLTIMA CONFIRMAÇÃO

Digite 'APLICAR' para confirmar: APLICAR

Aplicando migration...
Executando SQL...
✓ Migration aplicada com sucesso!

========================================
✅ Migration aplicada com sucesso!
========================================
```

## 📂 Criar Nova Migration

### 1. Criar arquivo SQL:

```bash
# migrations/add_email_verified_to_users.sql
ALTER TABLE users 
ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_users_email_verified ON users(email_verified);
```

### 2. Testar localmente (dev):

```bash
# Aplicar em ambiente de dev
./scripts/apply_migration.sh migrations/add_email_verified_to_users.sql
```

### 3. Aplicar em produção:

```bash
# SSH no servidor
ssh ignitor_online@34.42.168.19

# Fazer backup
./scripts/backup_db.sh

# Aplicar migration
./scripts/apply_migration.sh migrations/add_email_verified_to_users.sql
```

## 🔍 Verificar Migrations Aplicadas

### Ver todas as migrations:

```bash
# Conectar no banco
docker exec -it agents_postgres psql -U agentuser -d agentsdb

# Listar migrations aplicadas
SELECT * FROM schema_migrations ORDER BY applied_at DESC;
```

### Via script:

```bash
docker exec -it agents_postgres psql -U agentuser -d agentsdb -c \
  "SELECT migration_name, applied_at FROM schema_migrations;"
```

## 🚨 Troubleshooting

### Tabelas não foram criadas no primeiro deploy

```bash
# Verificar se banco está vazio
docker exec -it agents_postgres psql -U agentuser -d agentsdb
\dt

# Se vazio, criar manualmente
docker exec orkestrai-api python3 src/init_db.py

# Ou via script
./scripts/migrate_database.sh
```

### Migration falhou - reverter

```bash
# 1. Parar aplicação
docker stop orkestrai-api

# 2. Restaurar backup
cd ~/orkestrai-api
gunzip -c backups/backup_YYYYMMDD.sql.gz | \
  docker exec -i agents_postgres psql -U agentuser -d agentsdb

# 3. Remover registro da migration
docker exec -it agents_postgres psql -U agentuser -d agentsdb

DELETE FROM schema_migrations 
WHERE migration_name = 'nome_da_migration.sql';

# 4. Reiniciar aplicação
docker start orkestrai-api
```

### Forçar recriação de tabelas

```bash
# ⚠️ CUIDADO: Apaga TUDO!

# Parar aplicação
docker stop orkestrai-api

# Dropar e recriar banco
docker-compose down -v
docker-compose up -d postgres redis

# Aguardar PostgreSQL
sleep 10

# Deploy (criará tabelas)
./scripts/deploy_manual.sh
```

## 🔒 Boas Práticas

### ✅ **Faça:**

1. **Sempre fazer backup** antes de migrations
   ```bash
   ./scripts/backup_db.sh
   ```

2. **Testar em dev** antes de aplicar em produção

3. **Revisar SQL** cuidadosamente antes de confirmar

4. **Migrations pequenas e incrementais**
   ```sql
   -- BOM: Uma mudança por vez
   ALTER TABLE users ADD COLUMN phone VARCHAR(20);
   ```

5. **Nomear descritivamente**
   ```
   add_column_phone_to_users.sql
   create_index_on_agents_name.sql
   ```

6. **Documentar migrations complexas**
   ```sql
   -- Migration: Adicionar suporte a telefone
   -- Data: 2025-01-15
   -- Razão: Autenticação 2FA via SMS
   ALTER TABLE users ADD COLUMN phone VARCHAR(20);
   ```

### ❌ **Não faça:**

1. ❌ Aplicar migrations sem backup
2. ❌ Deletar dados sem MUITO cuidado
3. ❌ Modificar migrations já aplicadas
4. ❌ Aplicar múltiplas migrations grandes de uma vez
5. ❌ Migrations destrutivas sem plano de rollback

## 📊 Migrations SQL Existentes

Atualmente no projeto:

```bash
migrations/
├── add_use_file_search_to_agents.sql
└── fix_file_search_google_file_name.sql
```

Para aplicá-las em produção:

```bash
# Backup primeiro
./scripts/backup_db.sh

# Aplicar cada uma
./scripts/apply_migration.sh migrations/add_use_file_search_to_agents.sql
./scripts/apply_migration.sh migrations/fix_file_search_google_file_name.sql
```

## 🎯 Fluxo Completo

### Primeiro Deploy (Produção Vazia):

```
1. Deploy automático
   ↓
2. Verifica banco: vazio
   ↓
3. Cria todas as tabelas ✅
   ↓
4. Inicia API
   ↓
5. ✅ Pronto para usar!
```

### Deploy com Nova Feature:

```
1. Desenvolver nova feature
   ↓
2. Criar migration SQL (se necessário)
   ↓
3. Testar em dev
   ↓
4. Deploy automático (código)
   ↓
5. Aplicar migration manual (se necessário)
   └─ ./scripts/apply_migration.sh
   ↓
6. ✅ Feature disponível
```

## 🔧 Scripts Disponíveis

### `scripts/migrate_database.sh`
- Cria tabelas + aplica migrations
- **Use apenas em dev/teste**
- ❌ Não usar em produção

### `scripts/apply_migration.sh` ⭐
- Aplica migration SQL específica
- Múltiplas confirmações
- **Use em produção**
- ✅ Seguro e controlado

### `src/init_db.py`
- Cria apenas tabelas
- Sem migrations SQL
- Útil para reset completo

## 🌐 Ambiente Local vs Produção

### Local (Dev):
```bash
# Pode usar qualquer script
./scripts/migrate_database.sh
python src/init_db.py

# Ou resetar tudo
docker-compose down -v
docker-compose up -d
```

### Produção:
```bash
# 1. Primeiro deploy: automático ✅
# 2. Migrations SQL: sempre manual ✅

# Backup + aplicar migration
./scripts/backup_db.sh
./scripts/apply_migration.sh migrations/sua_migration.sql
```

## 📝 Resumo

✅ **Tabelas criadas automaticamente** apenas na primeira vez
✅ **Verificação segura** antes de criar (idempotente)
✅ **Migrations SQL sempre manuais** em produção
✅ **Backup obrigatório** antes de migrations
✅ **Múltiplas confirmações** para segurança
✅ **Controle de versão** em `schema_migrations`
✅ **Você tem controle total** sobre quando aplicar

**Não há risco de migrations automáticas deletarem dados! 🔒**

---

**Scripts relacionados:**
- `scripts/apply_migration.sh` - Aplicar migration manual (⭐ use este em produção)
- `scripts/migrate_database.sh` - Migrations automáticas (dev/teste)
- `scripts/backup_db.sh` - Backup do banco
- `src/init_db.py` - Criar tabelas iniciais
