# Migração do Banco de Dados - File Search

## Problema Identificado

O campo `google_file_name` na tabela `file_search_files` tinha:
- `nullable=False` (não permitia NULL)
- `unique=True` (deveria ser único)

Quando não conseguíamos extrair o nome do arquivo da resposta da operação do Google, salvávamos como string vazia (`''`). Isso causava violação da constraint de unicidade quando múltiplos arquivos eram enviados sem conseguir extrair o `google_file_name`.

## Solução Implementada

### Mudança no Modelo

**Antes:**
```python
google_file_name = Column(String(500), nullable=False, unique=True)
```

**Depois:**
```python
google_file_name = Column(String(500), nullable=True, unique=True)
```

### Mudança na Lógica de Salvamento

**Antes:**
```python
google_file_name=file_info.get('name', '')  # String vazia se não disponível
```

**Depois:**
```python
google_file_name = file_info.get('name', '').strip()
if not google_file_name:
    google_file_name = None  # Use None instead of empty string
```

## Migração do Banco de Dados

Se você já tem dados no banco, execute a seguinte migração SQL:

```sql
-- 1. Remover constraint de NOT NULL
ALTER TABLE file_search_files 
ALTER COLUMN google_file_name DROP NOT NULL;

-- 2. Atualizar strings vazias para NULL
UPDATE file_search_files 
SET google_file_name = NULL 
WHERE google_file_name = '';

-- 3. Verificar se há duplicatas (deve retornar 0 linhas)
SELECT google_file_name, COUNT(*) 
FROM file_search_files 
WHERE google_file_name IS NOT NULL 
GROUP BY google_file_name 
HAVING COUNT(*) > 1;
```

## Comportamento Após Migração

1. **Múltiplos arquivos sem `google_file_name`**: ✅ Permitido (todos terão `NULL`)
2. **Arquivos com `google_file_name`**: ✅ Devem ser únicos (constraint mantida)
3. **Extração do nome do arquivo**: 🔄 Continua tentando extrair, mas não falha se não conseguir

## Notas

- A constraint `unique=True` ainda funciona: permite múltiplos `NULL` (comportamento padrão do PostgreSQL)
- Quando conseguirmos extrair o `google_file_name` corretamente, ele será único
- O problema de extração do nome do arquivo ainda precisa ser resolvido (logs de debug foram adicionados)

