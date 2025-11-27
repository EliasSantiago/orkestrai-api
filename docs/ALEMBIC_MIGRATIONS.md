# 🗄️ Migrations com Alembic

Este projeto agora usa **Alembic** para gerenciar migrations de banco de dados, seguindo o padrão da comunidade Python.

## 📋 Por que Alembic?

- ✅ **Padrão da indústria**: Usado pela maioria dos projetos Python com SQLAlchemy
- ✅ **Versionamento automático**: Histórico completo de todas as mudanças
- ✅ **Rollback fácil**: Pode reverter migrations com `alembic downgrade`
- ✅ **Integração nativa**: Funciona perfeitamente com SQLAlchemy
- ✅ **Autogenerate**: Pode gerar migrations automaticamente a partir dos models
- ✅ **Controle de versão**: Rastreia quais migrations foram aplicadas

## 🚀 Como Funciona

### Durante o Deploy

As migrations são executadas **automaticamente** durante o deploy:

1. Deploy inicia
2. PostgreSQL fica pronto
3. **Alembic aplica todas as migrations pendentes**
4. API inicia

### Estrutura de Diretórios

```
orkestrai-api/
├── alembic/                    # Diretório principal do Alembic
│   ├── versions/              # Todas as migrations (histórico)
│   │   └── 523dbb60ecfe_update_free_plan_tokens_to_10000.py
│   ├── env.py                 # Configuração do Alembic
│   └── script.py.mako         # Template para novas migrations
├── alembic.ini                 # Configuração principal
└── scripts/
    └── run_alembic_migrations.sh  # Script executado no deploy
```

## 🛠️ Comandos Úteis

### Ver Status das Migrations

```bash
# Ver versão atual do banco
alembic current

# Ver todas as migrations (aplicadas e pendentes)
alembic history

# Ver migrations pendentes
alembic heads
```

### Criar Nova Migration

```bash
# Migration automática (a partir dos models)
alembic revision --autogenerate -m "descrição da mudança"

# Migration manual (SQL customizado)
alembic revision -m "descrição da mudança"
```

### Aplicar Migrations

```bash
# Aplicar todas as migrations pendentes
alembic upgrade head

# Aplicar até uma versão específica
alembic upgrade <revision_id>

# Aplicar próxima migration
alembic upgrade +1
```

### Reverter Migrations

```bash
# Reverter última migration
alembic downgrade -1

# Reverter até uma versão específica
alembic downgrade <revision_id>

# Reverter todas
alembic downgrade base
```

## 📝 Criando uma Nova Migration

### Exemplo: Adicionar Nova Coluna

1. **Edite o model** em `src/models.py`:
```python
class User(Base):
    # ... campos existentes ...
    phone = Column(String(20), nullable=True)  # Nova coluna
```

2. **Gere a migration**:
```bash
alembic revision --autogenerate -m "add_phone_to_users"
```

3. **Revise a migration gerada** em `alembic/versions/`:
```python
def upgrade():
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone')
```

4. **Teste localmente**:
```bash
alembic upgrade head
```

5. **Commit e push**: A migration será aplicada automaticamente no próximo deploy

### Exemplo: Migration Manual (SQL Customizado)

```bash
alembic revision -m "update_free_plan_tokens"
```

Edite o arquivo gerado:

```python
from alembic import op
from sqlalchemy import text

def upgrade():
    op.execute(text("""
        UPDATE plans 
        SET monthly_token_limit = 10000
        WHERE name = 'free'
    """))

def downgrade():
    op.execute(text("""
        UPDATE plans 
        SET monthly_token_limit = 2000
        WHERE name = 'free'
    """))
```

## 🔄 Migrations Existentes

### Migration Atual

- **`523dbb60ecfe_update_free_plan_tokens_to_10000`**: Atualiza limite do plano free para 10.000 tokens

## ⚠️ Importante

1. **Nunca edite migrations já aplicadas**: Crie uma nova migration para corrigir problemas
2. **Sempre teste localmente**: Antes de fazer deploy
3. **Backup em produção**: Antes de migrations grandes
4. **Downgrade sempre implementado**: Sempre implemente a função `downgrade()` para poder reverter

## 🔍 Troubleshooting

### Migration falhou no deploy

1. Verifique os logs do deploy
2. Conecte ao servidor e execute manualmente:
```bash
docker exec orkestrai-api alembic current
docker exec orkestrai-api alembic upgrade head
```

### Conflito de versão

Se houver conflito de versões:
```bash
# Ver versão atual
alembic current

# Verificar histórico
alembic history

# Aplicar manualmente
alembic upgrade head
```

## 📚 Referências

- [Documentação Alembic](https://alembic.sqlalchemy.org/)
- [Tutorial Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy Migrations](https://docs.sqlalchemy.org/en/20/core/metadata.html)

