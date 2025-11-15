# Estratégia de IDs e Segurança

## 📋 Decisão sobre IDs de Usuário

### IDs Sequenciais vs UUID

**Decisão: Manter IDs Sequenciais (Integer)**

### Análise

#### IDs Sequenciais (Integer) - ✅ Escolhido
**Vantagens:**
- ✅ **Performance**: Mais rápido para joins e índices
- ✅ **Armazenamento**: Menor uso de espaço (4 bytes vs 16 bytes)
- ✅ **Legibilidade**: Mais fácil de debugar e referenciar
- ✅ **Simplicidade**: Mais fácil de trabalhar em queries SQL
- ✅ **Escalabilidade**: PostgreSQL lida bem com bigint (até 9.223.372.036.854.775.807)

**Desvantagens:**
- ⚠️ **Enumeração**: Possível enumerar usuários (mitigado com autenticação)
- ⚠️ **Informação**: IDs revelam quantidade de usuários (mitigado com rate limiting)

#### UUID - ❌ Não escolhido
**Vantagens:**
- ✅ **Segurança**: Não revela quantidade de usuários
- ✅ **Unicidade**: Garantido globalmente
- ✅ **Distribuição**: Melhor para sistemas distribuídos

**Desvantagens:**
- ❌ **Performance**: Mais lento em joins e índices
- ❌ **Armazenamento**: 4x maior (16 bytes vs 4 bytes)
- ❌ **Legibilidade**: Mais difícil de debugar
- ❌ **Complexidade**: Mais difícil de trabalhar

### Práticas de Grandes Aplicações

**Análise de grandes aplicações:**

1. **GitHub**: Usa IDs sequenciais para usuários
2. **Twitter/X**: Usa IDs sequenciais (snowflake para tweets)
3. **Facebook**: Usa IDs sequenciais
4. **Google**: Usa IDs sequenciais para muitos serviços
5. **Amazon**: Usa IDs sequenciais para usuários

**Conclusão**: A maioria das grandes aplicações usa IDs sequenciais para entidades principais (usuários, agentes) porque:
- Performance é crítica em escala
- Segurança é garantida por autenticação/autorização, não por ofuscação de IDs
- Simplicidade facilita manutenção

### Nossa Estratégia

**Manter IDs Sequenciais com:**
1. ✅ **Autenticação obrigatória** em todos os endpoints
2. ✅ **Validação de propriedade** em todas as operações (sempre filtrar por `user_id`)
3. ✅ **Rate limiting** para prevenir enumeração
4. ✅ **Logs de auditoria** para detectar acesso não autorizado
5. ✅ **Mensagens de erro genéricas** (404 em vez de 403) para evitar informação

## 🔒 Segurança de Isolamento

### Princípios Implementados

1. **Sempre filtrar por `user_id`**:
   ```python
   # ✅ CORRETO
   store = db.query(FileSearchStore).filter(
       FileSearchStore.id == store_id,
       FileSearchStore.user_id == user_id  # CRITICAL
   ).first()
   
   # ❌ ERRADO - Nunca fazer isso
   store = db.query(FileSearchStore).filter(
       FileSearchStore.id == store_id
   ).first()
   ```

2. **Validação em múltiplas camadas**:
   - ✅ Autenticação (JWT token)
   - ✅ Autorização (verificação de propriedade)
   - ✅ Filtros de banco de dados

3. **Mensagens de erro genéricas**:
   - ✅ Retornar 404 (Not Found) em vez de 403 (Forbidden)
   - ✅ Evitar revelar que um recurso existe mas pertence a outro usuário

### Endpoints Protegidos

Todos os endpoints de File Search verificam propriedade:

- ✅ `GET /api/file-search/stores` - Filtra por `user_id`
- ✅ `GET /api/file-search/stores/{id}` - Verifica `user_id`
- ✅ `POST /api/file-search/stores/{id}/files` - Verifica `user_id` do store
- ✅ `GET /api/file-search/stores/{id}/files` - Verifica `user_id` do store
- ✅ `GET /api/file-search/stores/{id}/files/{file_id}` - Verifica `user_id` do store
- ✅ `DELETE /api/file-search/stores/{id}/files/{file_id}` - Verifica `user_id` do store
- ✅ `DELETE /api/file-search/stores/{id}` - Verifica `user_id`

## 🆔 Session IDs

### Formato: UUID v4

**Formato anterior**: `session_abc123` (12 hex chars)
**Formato novo**: `cc9e7f12-0413-49bc-91dd-7a5f6f2500da` (UUID v4)

### Vantagens do UUID para Sessions

1. ✅ **Unicidade garantida**: UUID v4 tem 122 bits de entropia
2. ✅ **Não sequencial**: Não revela quantidade de sessões
3. ✅ **Padrão da indústria**: Formato reconhecido universalmente
4. ✅ **Segurança**: Muito difícil de adivinhar ou enumerar
5. ✅ **Distribuição**: Funciona bem em sistemas distribuídos

### Implementação

```python
import uuid

def generate_session_id() -> str:
    """Generate a session ID using UUID format."""
    return str(uuid.uuid4())
```

**Exemplo**: `cc9e7f12-0413-49bc-91dd-7a5f6f2500da`

## 📊 Resumo

| Aspecto | Decisão | Justificativa |
|---------|---------|---------------|
| **User IDs** | Sequenciais (Integer) | Performance, simplicidade, padrão da indústria |
| **Session IDs** | UUID v4 | Segurança, unicidade, não sequencial |
| **Isolamento** | Filtro por `user_id` em todas as queries | Segurança em múltiplas camadas |
| **Mensagens de Erro** | Genéricas (404) | Evitar informação sobre outros usuários |

## ✅ Checklist de Segurança

- [x] Todos os endpoints verificam autenticação
- [x] Todos os endpoints filtram por `user_id`
- [x] Mensagens de erro são genéricas
- [x] Session IDs usam UUID v4
- [x] Logs de auditoria implementados
- [x] Validação em múltiplas camadas

