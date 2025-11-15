# TTL de 1 Hora - Exemplos Práticos

## 🕐 O que acontece com TTL de 1 hora (3600 segundos)

### Comportamento Técnico

Quando você configura `CONVERSATION_TTL=3600` (1 hora):

1. **Dados no Redis expiram após 1 hora de inatividade**
2. **Sistema faz fallback para PostgreSQL** (dados permanentes)
3. **Usuário pode continuar conversando** (dados são recuperados do PostgreSQL)

## 📋 Exemplos Práticos

### Exemplo 1: Conversa Contínua (Dentro de 1 hora)

**Cenário**: Usuário conversa com agente por 30 minutos

```
10:00 - Usuário: "Olá, preciso agendar uma reunião"
       ✅ Mensagem salva no Redis (TTL: 1h, expira às 11:00)
       ✅ Mensagem salva no PostgreSQL (permanente)

10:05 - Agente: "Claro! Para quando você gostaria?"
       ✅ Resposta salva no Redis (TTL: 1h, expira às 11:05)
       ✅ Resposta salva no PostgreSQL (permanente)

10:10 - Usuário: "Para amanhã às 14h"
       ✅ Mensagem salva no Redis (TTL: 1h, expira às 11:10)
       ✅ TTL é renovado automaticamente a cada mensagem
       ✅ Mensagem salva no PostgreSQL (permanente)

10:15 - Agente: "Perfeito! Reunião agendada"
       ✅ Resposta salva no Redis (TTL: 1h, expira às 11:15)
       ✅ Resposta salva no PostgreSQL (permanente)
```

**Resultado**: ✅ Tudo funciona normalmente, dados no Redis são renovados a cada interação

---

### Exemplo 2: Usuário Volta Após 1 Hora de Inatividade

**Cenário**: Usuário conversa, sai, e volta após 1h15min

```
10:00 - Usuário: "Agende uma reunião para amanhã"
       ✅ Salvo no Redis (expira às 11:00)
       ✅ Salvo no PostgreSQL

10:05 - Agente: "Reunião agendada com sucesso"
       ✅ Salvo no Redis (expira às 11:05)
       ✅ Salvo no PostgreSQL

[Usuário sai e volta após 1h15min]

11:20 - Usuário: "Qual foi o horário da reunião?"
       ⚠️ Redis: Dados expirados (não encontrados)
       ✅ PostgreSQL: Dados ainda disponíveis
       ✅ Sistema recupera histórico do PostgreSQL automaticamente
       ✅ Agente responde: "A reunião está agendada para amanhã às 14h"
       ✅ Nova mensagem salva no Redis (expira às 12:20)
       ✅ Nova mensagem salva no PostgreSQL
```

**Resultado**: ✅ Funciona normalmente, mas com latência ligeiramente maior (PostgreSQL é mais lento que Redis)

---

### Exemplo 3: Conversa Muito Longa (Mais de 1 hora)

**Cenário**: Usuário conversa continuamente por 2 horas

```
10:00 - Usuário: "Vou fazer várias perguntas"
       ✅ Redis: Salvo (expira às 11:00)

10:30 - Usuário: "Primeira pergunta..."
       ✅ Redis: Salvo (expira às 11:30)
       ✅ TTL renovado automaticamente

11:00 - Usuário: "Segunda pergunta..."
       ✅ Redis: Dados anteriores expiraram, mas novos são salvos
       ✅ PostgreSQL: Todas as mensagens anteriores ainda disponíveis
       ✅ Sistema recupera contexto do PostgreSQL quando necessário

11:30 - Usuário: "Terceira pergunta..."
       ✅ Redis: Salvo (expira às 12:30)
       ✅ PostgreSQL: Todas as mensagens disponíveis
```

**Resultado**: ✅ Funciona, mas mensagens antigas (>1h) não estão no cache Redis, apenas no PostgreSQL

---

### Exemplo 4: Múltiplas Sessões do Mesmo Usuário

**Cenário**: Usuário tem 3 sessões diferentes

```
Sessão A (criada 10:00):
10:00 - "Pergunta sobre produto X"
       ✅ Redis: Salvo (expira às 11:00)
       ✅ PostgreSQL: Salvo

Sessão B (criada 10:30):
10:30 - "Pergunta sobre produto Y"
       ✅ Redis: Salvo (expira às 11:30)
       ✅ PostgreSQL: Salvo

Sessão C (criada 11:00):
11:00 - "Pergunta sobre produto Z"
       ✅ Redis: Salvo (expira às 12:00)
       ✅ PostgreSQL: Salvo

11:15 - Usuário volta à Sessão A:
       ⚠️ Redis: Dados expirados (não encontrados)
       ✅ PostgreSQL: Dados disponíveis
       ✅ Sistema recupera do PostgreSQL
       ✅ Agente continua conversa normalmente
```

**Resultado**: ✅ Cada sessão expira independentemente, mas dados permanecem no PostgreSQL

---

## ⚡ Impacto na Performance

### Com TTL de 1 hora

| Situação | Fonte de Dados | Latência | Experiência |
|----------|----------------|----------|-------------|
| **Conversa ativa (< 1h)** | Redis | < 1ms | ⚡ Excelente |
| **Conversa após 1h** | PostgreSQL | 5-20ms | ✅ Boa (ligeiramente mais lento) |
| **Primeira mensagem** | PostgreSQL | 5-20ms | ✅ Boa |

### Comparação: 1h vs 4h

| Aspecto | 1 hora | 4 horas |
|---------|--------|---------|
| **Cache Hit Rate** | ~70% | ~90% |
| **Latência Média** | 3-5ms | 1-2ms |
| **Uso de PostgreSQL** | Mais frequente | Menos frequente |
| **Segurança** | ⭐⭐⭐ Máxima | ⭐⭐ Alta |

## 🔄 Fluxo de Recuperação de Dados

### Quando Redis Expira

```
1. Usuário faz requisição
   ↓
2. Sistema tenta buscar no Redis
   ↓
3. Redis retorna: "Chave não encontrada" (expirada)
   ↓
4. Sistema faz fallback automático para PostgreSQL
   ↓
5. Dados são recuperados do PostgreSQL
   ↓
6. Resposta é gerada normalmente
   ↓
7. Nova mensagem é salva no Redis (com novo TTL de 1h)
   ↓
8. Nova mensagem é salva no PostgreSQL
```

**Resultado**: ✅ Transparente para o usuário, apenas latência ligeiramente maior

## 📊 Exemplos de Uso Real

### Caso 1: Suporte ao Cliente

```
09:00 - Cliente: "Tenho um problema com meu pedido"
       ✅ Redis: Cache ativo

09:30 - Agente: "Pode me dar mais detalhes?"
       ✅ Redis: Cache ativo

10:00 - Cliente: "O pedido não chegou"
       ✅ Redis: Cache ativo (renovado)

10:30 - Agente: "Vou verificar para você"
       ✅ Redis: Cache ativo

[Cliente volta 2 horas depois]

12:30 - Cliente: "E aí, o que descobriu?"
       ⚠️ Redis: Cache expirado (última mensagem foi há 2h)
       ✅ PostgreSQL: Todas as mensagens disponíveis
       ✅ Agente: "Encontrei o problema! Seu pedido está em trânsito"
       ✅ Nova mensagem salva no Redis (expira às 13:30)
```

**Impacto**: ✅ Funciona perfeitamente, apenas primeira resposta após 1h é um pouco mais lenta

---

### Caso 2: Assistente de Produtividade

```
08:00 - Usuário: "Crie um evento para hoje às 15h"
       ✅ Redis: Cache ativo

08:05 - Agente: "Evento criado com sucesso"
       ✅ Redis: Cache ativo

[Usuário trabalha em outras coisas]

09:10 - Usuário: "Qual evento criei hoje?"
       ⚠️ Redis: Cache expirado (última mensagem foi há 1h05min)
       ✅ PostgreSQL: Dados disponíveis
       ✅ Agente: "Você criou um evento para hoje às 15h"
       ✅ Nova mensagem salva no Redis (expira às 10:10)
```

**Impacto**: ✅ Funciona, mas usuário pode notar leve delay na primeira resposta

---

### Caso 3: Chat de Vendas

```
14:00 - Cliente: "Quanto custa o produto X?"
       ✅ Redis: Cache ativo

14:10 - Vendedor: "R$ 500,00 com desconto"
       ✅ Redis: Cache ativo

14:20 - Cliente: "Tem parcelamento?"
       ✅ Redis: Cache ativo (renovado)

14:30 - Vendedor: "Sim, até 10x sem juros"
       ✅ Redis: Cache ativo

[Cliente pensa e volta 1h30 depois]

16:00 - Cliente: "Quero comprar, como faço?"
       ⚠️ Redis: Cache expirado
       ✅ PostgreSQL: Todas as mensagens disponíveis
       ✅ Vendedor: "Perfeito! Vou te passar o link de compra"
       ✅ Nova mensagem salva no Redis (expira às 17:00)
```

**Impacto**: ✅ Funciona, mas primeira resposta após 1h pode ter delay de 50-100ms

---

## ⚠️ Pontos de Atenção

### 1. Performance em Conversas Longas

**Problema**: Em conversas muito longas (>1h), mensagens antigas não estão no cache

**Solução**: Sistema já faz fallback automático para PostgreSQL

**Impacto**: Latência de 5-20ms em vez de <1ms (imperceptível para usuários)

### 2. Múltiplas Sessões Simultâneas

**Problema**: Cada sessão expira independentemente

**Solução**: Cada sessão é gerenciada separadamente, dados permanecem no PostgreSQL

**Impacto**: Nenhum, funciona normalmente

### 3. Primeira Mensagem Após Expiração

**Problema**: Primeira mensagem após 1h precisa buscar do PostgreSQL

**Solução**: Sistema faz isso automaticamente, usuário não percebe

**Impacto**: Delay de 50-100ms na primeira resposta (aceitável)

---

## ✅ Vantagens do TTL de 1 Hora

1. ✅ **Máxima Segurança**: Dados sensíveis expiram rapidamente
2. ✅ **Conformidade GDPR/LGPD**: Minimiza retenção de dados
3. ✅ **Reduz Risco**: Janela de exposição muito pequena
4. ✅ **Funcionalidade Preservada**: Dados permanecem no PostgreSQL
5. ✅ **Transparente**: Usuário não percebe a diferença na maioria dos casos

---

## ⚠️ Desvantagens do TTL de 1 Hora

1. ⚠️ **Cache Hit Rate Menor**: ~70% vs ~90% com 4h
2. ⚠️ **Mais Acessos ao PostgreSQL**: Mais carga no banco
3. ⚠️ **Latência Ligeiramente Maior**: 3-5ms vs 1-2ms (média)
4. ⚠️ **Usuários Inativos**: Precisam esperar recuperação do PostgreSQL

---

## 🎯 Recomendação Final

### Use TTL de 1 Hora Se:
- ✅ Você lida com dados altamente sensíveis (CPF, cartões, etc.)
- ✅ Conformidade regulatória é crítica
- ✅ Você está disposto a aceitar leve aumento de latência
- ✅ Você quer máxima segurança

### Use TTL de 4 Horas Se:
- ✅ Você quer balance entre segurança e performance
- ✅ Dados são moderadamente sensíveis
- ✅ Você quer melhor experiência do usuário
- ✅ Você quer menos carga no PostgreSQL

---

## 🔧 Como Configurar

### Opção 1: Via Variável de Ambiente

```bash
# No arquivo .env
CONVERSATION_TTL=3600  # 1 hora em segundos
```

### Opção 2: Via Código (temporário para teste)

```python
# src/config.py
CONVERSATION_TTL = int(os.getenv("CONVERSATION_TTL", "3600"))  # 1 hora
```

---

## 📈 Métricas Esperadas

Com TTL de 1 hora, você pode esperar:

- **Cache Hit Rate**: ~70-75% (vs ~90% com 4h)
- **Latência Média**: 3-5ms (vs 1-2ms com 4h)
- **Acessos PostgreSQL**: ~25-30% das requisições (vs ~10% com 4h)
- **Experiência do Usuário**: Boa (delay imperceptível na maioria dos casos)

---

## 🧪 Como Testar

1. **Configure TTL de 1 hora**:
   ```bash
   echo "CONVERSATION_TTL=3600" >> .env
   ```

2. **Inicie uma conversa**:
   ```bash
   curl -X POST 'http://localhost:8001/api/agents/chat' \
     -H 'Authorization: Bearer TOKEN' \
     -d '{"agent_id": 1, "message": "Olá"}'
   ```

3. **Aguarde 1h10min e envie outra mensagem**:
   ```bash
   # Após 1h10min
   curl -X POST 'http://localhost:8001/api/agents/chat' \
     -H 'Authorization: Bearer TOKEN' \
     -d '{"agent_id": 1, "message": "Lembra da nossa conversa?", "session_id": "SESSION_ID"}'
   ```

4. **Observe**: Sistema recupera do PostgreSQL automaticamente

---

## 💡 Conclusão

**TTL de 1 hora funciona perfeitamente**, mas com trade-offs:

- ✅ **Segurança**: Máxima
- ✅ **Funcionalidade**: Preservada (fallback automático)
- ⚠️ **Performance**: Ligeiramente menor (mas ainda excelente)
- ⚠️ **Carga no Banco**: Maior (mas gerenciável)

**Recomendação**: Use 1 hora se segurança é prioridade, use 4 horas se quer balance ideal.

