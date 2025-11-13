# Retenção de Dados e Segurança - Análise e Recomendações

## 📊 Situação Atual

### Tempo de Expiração das Sessions no Redis

**Atual**: 24 horas (86400 segundos)

**Onde está configurado:**
1. `src/config.py`: `CONVERSATION_TTL = 86400` (24 horas)
2. `src/adk_conversation_middleware.py`: `setex(..., 86400, ...)` (24 horas)
3. `src/redis_client.py`: Usa `Config.CONVERSATION_TTL` para expiração

### Dados Armazenados no Redis

**Dados de Sessão:**
- `session:user_id:{session_id}` → `user_id` (24h)
- `conversation:user:{user_id}:session:{session_id}` → Mensagens da conversa (24h)
- `sessions:user:{user_id}` → Lista de session_ids do usuário (24h)

**Dados Pessoais (PII) Potencialmente Armazenados:**
- ✅ **Mensagens de conversa**: Podem conter informações pessoais mencionadas pelo usuário
- ✅ **Session IDs**: Identificadores de sessão
- ✅ **User IDs**: Identificadores de usuário
- ⚠️ **Conteúdo de mensagens**: Pode incluir CPF, nome, endereço, telefone, email, etc. se o usuário mencionar

## 🔍 Padrões de Grandes Empresas

### Análise de Práticas da Indústria

| Empresa/Serviço | TTL de Sessão | Justificativa |
|----------------|---------------|---------------|
| **Oracle SSO** | 8 horas | Segurança para sistemas corporativos |
| **Adobe Commerce** | 10 min - 30 dias | Varia por tipo de sessão |
| **Bancos (geral)** | 15-30 minutos | Dados altamente sensíveis |
| **E-commerce** | 1-7 dias | Balance entre UX e segurança |
| **Redes Sociais** | 30-90 dias | Experiência do usuário |
| **Aplicações SaaS** | 1-24 horas | Balance padrão |

### Recomendações por Tipo de Dado

#### Dados Altamente Sensíveis (CPF, Cartão de Crédito, Senhas)
- **TTL Recomendado**: 15-30 minutos
- **Justificativa**: Minimizar janela de exposição em caso de vazamento

#### Dados Moderadamente Sensíveis (Email, Telefone, Endereço)
- **TTL Recomendado**: 1-4 horas
- **Justificativa**: Balance entre segurança e experiência

#### Dados de Conversa (Mensagens de Chat)
- **TTL Recomendado**: 1-8 horas
- **Justificativa**: Depende do conteúdo, mas geralmente 2-4 horas é seguro

#### Session Metadata (IDs, timestamps)
- **TTL Recomendado**: 4-24 horas
- **Justificativa**: Menos sensível, mas ainda deve expirar

## ⚖️ Conformidade Regulatória

### GDPR (Europa)
- **Princípio de Minimização**: Armazenar apenas o necessário
- **Princípio de Limitação de Finalidade**: Dados apenas para propósito específico
- **Retenção Limitada**: Dados devem ser deletados quando não mais necessários
- **Recomendação**: TTL de 1-4 horas para dados de conversa

### LGPD (Brasil)
- **Princípio de Finalidade**: Dados apenas para finalidade específica
- **Princípio de Necessidade**: Apenas dados necessários
- **Princípio de Segurança**: Medidas técnicas adequadas
- **Recomendação**: TTL de 1-4 horas para dados de conversa

### PCI DSS (Cartões de Crédito)
- **Requisito**: Dados de cartão não devem ser armazenados em cache
- **Recomendação**: Se processar pagamentos, TTL de 15 minutos ou menos

## 🎯 Recomendações para Nossa Aplicação

### Cenário 1: Aplicação Geral (Chat/Agentes)
**Recomendação**: **Reduzir para 4 horas (14400 segundos)**

**Justificativa:**
- ✅ Balance entre segurança e experiência do usuário
- ✅ Reduz significativamente janela de exposição (de 24h para 4h)
- ✅ Ainda permite sessões longas de trabalho
- ✅ Alinhado com práticas de SaaS modernas
- ✅ Conformidade com GDPR/LGPD

**Impacto:**
- ⚠️ Usuários inativos por mais de 4 horas precisarão iniciar nova sessão
- ✅ Dados sensíveis expiram mais rápido
- ✅ Reduz risco de exposição em caso de vazamento

### Cenário 2: Aplicação com Dados Altamente Sensíveis
**Recomendação**: **Reduzir para 1 hora (3600 segundos)**

**Justificativa:**
- ✅ Máxima segurança para dados pessoais
- ✅ Alinhado com práticas bancárias
- ✅ Minimiza janela de exposição

**Impacto:**
- ⚠️ Usuários precisarão reautenticar mais frequentemente
- ✅ Máxima proteção de dados

### Cenário 3: Aplicação com Dados Não Sensíveis
**Recomendação**: **Manter 24 horas ou reduzir para 8 horas**

**Justificativa:**
- ✅ Melhor experiência do usuário
- ✅ Apropriado se não houver dados sensíveis

## 🔒 Implementação Recomendada

### Opção 1: TTL Configurável por Tipo de Dado (Recomendado)

```python
# src/config.py
class Config:
    # TTL para diferentes tipos de dados
    CONVERSATION_TTL = int(os.getenv("CONVERSATION_TTL", "14400"))  # 4 horas (padrão)
    SESSION_METADATA_TTL = int(os.getenv("SESSION_METADATA_TTL", "14400"))  # 4 horas
    USER_ID_MAPPING_TTL = int(os.getenv("USER_ID_MAPPING_TTL", "14400"))  # 4 horas
    
    # Para dados altamente sensíveis (se necessário)
    SENSITIVE_DATA_TTL = int(os.getenv("SENSITIVE_DATA_TTL", "3600"))  # 1 hora
```

### Opção 2: TTL Único Reduzido (Mais Simples)

```python
# src/config.py
class Config:
    # Reduzir de 24h para 4h
    CONVERSATION_TTL = int(os.getenv("CONVERSATION_TTL", "14400"))  # 4 horas
```

## 📋 Checklist de Segurança

### Dados Pessoais (PII) Identificados

- [x] **Mensagens de conversa**: Podem conter qualquer informação pessoal
- [x] **Session IDs**: Identificadores (menos sensível)
- [x] **User IDs**: Identificadores (menos sensível)
- [ ] **CPF**: Não armazenado diretamente (mas pode estar em mensagens)
- [ ] **Email**: Armazenado no PostgreSQL, não no Redis
- [ ] **Senhas**: Nunca armazenadas (apenas hash)
- [ ] **Cartões de Crédito**: Não processados

### Medidas de Segurança Implementadas

- [x] TTL automático no Redis (expiração automática)
- [x] Isolamento por usuário (filtros por user_id)
- [x] Autenticação obrigatória (JWT tokens)
- [x] PostgreSQL como backup permanente (com controle de retenção)
- [ ] Criptografia em trânsito (HTTPS - deve ser configurado)
- [ ] Criptografia em repouso (Redis - deve ser configurado em produção)

## 🚀 Plano de Ação Recomendado

### Fase 1: Redução Imediata (Recomendado)
1. ✅ Reduzir `CONVERSATION_TTL` de 86400 (24h) para **14400 (4h)**
2. ✅ Atualizar `adk_conversation_middleware.py` para usar valor configurável
3. ✅ Documentar mudança e impacto

### Fase 2: Melhorias Adicionais (Opcional)
1. ⚠️ Implementar TTL diferenciado por tipo de dado
2. ⚠️ Adicionar opção de "lembrar-me" (TTL estendido para usuários que optarem)
3. ⚠️ Implementar limpeza proativa de dados antigos
4. ⚠️ Adicionar logs de auditoria para acesso a dados sensíveis

### Fase 3: Conformidade (Se necessário)
1. ⚠️ Implementar política de retenção de dados
2. ⚠️ Adicionar funcionalidade de "esquecer meus dados" (GDPR)
3. ⚠️ Implementar criptografia em repouso para Redis
4. ⚠️ Adicionar monitoramento de acesso a dados sensíveis

## 📊 Comparação: Antes vs Depois

| Aspecto | Atual (24h) | Recomendado (4h) | Impacto |
|---------|--------------|-------------------|---------|
| **Janela de Exposição** | 24 horas | 4 horas | ✅ Redução de 83% |
| **Experiência do Usuário** | Excelente | Boa | ⚠️ Leve impacto |
| **Conformidade GDPR/LGPD** | Parcial | ✅ Melhor | ✅ Melhor |
| **Segurança** | Boa | ✅ Melhor | ✅ Melhor |
| **Risco de Vazamento** | Médio | ✅ Baixo | ✅ Reduzido |

## ✅ Decisão Final Recomendada

**Reduzir TTL de 24 horas para 4 horas (14400 segundos)**

**Razões:**
1. ✅ Reduz significativamente janela de exposição (83% de redução)
2. ✅ Ainda permite sessões longas de trabalho (4 horas)
3. ✅ Alinhado com práticas modernas de SaaS
4. ✅ Melhor conformidade com GDPR/LGPD
5. ✅ Impacto mínimo na experiência do usuário
6. ✅ Fácil de implementar (mudança de configuração)

**Alternativa Conservadora**: Se quiser máxima segurança, reduzir para **1 hora (3600 segundos)**

