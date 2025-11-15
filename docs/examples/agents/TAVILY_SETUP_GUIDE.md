# Guia de Configuração - Tavily Search API

## 🔍 O que é Tavily?

**Tavily** é uma API de busca otimizada especificamente para aplicações de IA e agentes. Diferente de buscadores tradicionais, o Tavily:

- ✅ Retorna resultados estruturados e limpos (perfeito para LLMs)
- ✅ Filtra spam e conteúdo de baixa qualidade
- ✅ Fornece resumos e snippets relevantes
- ✅ Suporta busca em tempo real
- ✅ Ideal para RAG (Retrieval-Augmented Generation)

**Site oficial**: https://tavily.com/

---

## 🚀 Configuração Passo a Passo

### 1. Criar Conta no Tavily

1. Acesse: https://tavily.com/
2. Clique em "Get Started" ou "Sign Up"
3. Crie sua conta (gratuita)
4. Confirme seu email

### 2. Obter API Key

1. Faça login em: https://app.tavily.com/
2. Vá em "API Keys" no menu
3. Copie sua API key (formato: `tvly-...`)

### 3. Configurar no Projeto

Edite o arquivo `.env` na raiz do projeto:

```bash
# Tavily Search API
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ Importante**: Mantenha sua API key em segredo! Não comita no git.

### 4. Verificar Configuração

```bash
# Verificar se a variável está configurada
python -c "from src.config import Config; print(f'Tavily API Key: {\"✅ Configurada\" if Config.TAVILY_API_KEY else \"❌ Não configurada\"}')"
```

---

## 📊 Planos e Limites

### Plano Gratuito
- ✅ **1.000 requisições/mês**
- ✅ Acesso a todas as features
- ✅ Sem cartão de crédito necessário
- ⚠️ Limite: ~33 buscas/dia

### Plano Pago (a partir de $20/mês)
- ✅ 10.000+ requisições/mês
- ✅ Prioridade no processamento
- ✅ Suporte técnico

**Dica**: Monitore seu uso em https://app.tavily.com/usage

---

## 🎯 Como Usar

### 1. Criar Agente com Tavily

```bash
# Via cURL
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @examples/agents/tavily_web_researcher.json

# Retorna: { "id": 15, "name": "Pesquisador Web - Tavily", ... }
```

### 2. Fazer Buscas

```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 15,
    "message": "Quais são as últimas notícias sobre inteligência artificial?",
    "session_id": ""
  }'
```

### 3. Exemplos de Prompts

#### Notícias Recentes
```
"Busque as últimas notícias sobre [tópico]"
"O que está acontecendo hoje em [área]?"
"Quais são as principais manchetes sobre [assunto]?"
```

#### Verificação de Fatos
```
"É verdade que [afirmação]? Por favor, verifique."
"Pode confirmar se [informação] está correto?"
```

#### Pesquisa Técnica
```
"Quais são as novidades sobre [tecnologia]?"
"Como funciona [conceito]? Busque informações atualizadas."
"Compare [produto A] vs [produto B] com dados recentes"
```

#### Dados Estatísticos
```
"Quais são os dados mais recentes sobre [métrica]?"
"Busque estatísticas atualizadas sobre [tópico]"
```

---

## 🔧 Exemplos de Agentes Disponíveis

### 1. Pesquisador Web Geral
**Arquivo**: `tavily_web_researcher.json`

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -d @examples/agents/tavily_web_researcher.json
```

**Casos de uso**:
- Pesquisa acadêmica
- Busca de informações gerais
- Verificação de dados
- Pesquisa de mercado

**Exemplo**:
```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 15,
    "message": "Busque informações sobre energia solar no Brasil em 2024"
  }'
```

### 2. Analista de Notícias
**Arquivo**: `tavily_news_analyst.json`

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -d @examples/agents/tavily_news_analyst.json
```

**Casos de uso**:
- Monitoramento de notícias
- Análise de eventos
- Briefings diários
- Due diligence

**Exemplo**:
```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 16,
    "message": "Faça um resumo das principais notícias sobre IA desta semana"
  }'
```

### 3. Verificador de Fatos
**Arquivo**: `tavily_fact_checker.json`

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -d @examples/agents/tavily_fact_checker.json
```

**Casos de uso**:
- Fact-checking
- Combate à desinformação
- Verificação de fontes
- Jornalismo investigativo

**Exemplo**:
```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 17,
    "message": "Verifique: A inteligência artificial vai substituir 85 milhões de empregos até 2025"
  }'
```

### 4. Scout Tecnológico
**Arquivo**: `tavily_tech_scout.json`

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -d @examples/agents/tavily_tech_scout.json
```

**Casos de uso**:
- Monitoramento de tendências tech
- Rastreamento de lançamentos
- Análise de competidores
- Scouting de inovações

**Exemplo**:
```bash
curl -X POST http://localhost:8001/api/agents/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent_id": 18,
    "message": "Quais são os principais lançamentos de IA desta semana?"
  }'
```

---

## 🎯 Boas Práticas

### 1. Otimize suas Buscas

```
❌ Ruim: "buscar informações"
✅ Bom: "Busque dados de mercado sobre carros elétricos no Brasil em 2024"

❌ Ruim: "o que está acontecendo?"
✅ Bom: "Quais são as últimas notícias sobre política econômica no Brasil?"
```

### 2. Gestão de Quota

- 📊 Monitore seu uso em https://app.tavily.com/usage
- ⚠️ Plano gratuito: ~33 buscas/dia (1000/mês)
- 💡 Cache resultados quando possível
- 🎯 Seja específico nas buscas para aproveitar melhor

### 3. Combine com Outras Tools

```json
{
  "tools": ["web_search", "calculator", "time"]
}
```

Exemplo:
- `web_search`: Buscar dados atualizados
- `calculator`: Fazer cálculos com os dados
- `time`: Contextualizar informações temporais

---

## 🐛 Troubleshooting

### Erro: "web_search tool not found"

**Causa**: Tool não está disponível

**Solução**:
1. Verifique se `TAVILY_API_KEY` está configurada no `.env`
2. Reinicie a aplicação
3. Verifique logs de inicialização

### Erro: "API key invalid"

**Causa**: API key incorreta ou expirada

**Solução**:
1. Verifique se copiou a key corretamente
2. Verifique se não tem espaços extras
3. Gere nova key em https://app.tavily.com/

### Erro: "Rate limit exceeded"

**Causa**: Atingiu limite de requisições

**Solução**:
1. Aguarde até o próximo ciclo (mensal)
2. Considere upgrade do plano
3. Otimize suas buscas

### Busca não retorna resultados

**Possíveis causas**:
- Query muito específica
- Idioma não suportado
- Conteúdo muito recente

**Soluções**:
- Torne a query mais genérica
- Use termos em inglês quando possível
- Tente variações da busca

---

## 📊 Comparação: Tavily vs Google Custom Search

| Aspecto | Tavily | Google Custom Search |
|---------|--------|---------------------|
| **Otimizado para IA** | ✅ Sim | ❌ Não |
| **Resultados limpos** | ✅ Sim | ⚠️ Requer processamento |
| **Quota gratuita** | 1.000/mês | 100/dia |
| **Facilidade de uso** | ✅ Fácil | ⚠️ Configuração complexa |
| **Qualidade para LLMs** | ✅ Excelente | ⚠️ Boa |
| **Preço (pago)** | $20+/mês | $5/1000 queries |

**Recomendação**: Use Tavily para aplicações com IA/LLMs.

---

## 📚 Recursos Adicionais

### Documentação
- **Tavily Docs**: https://docs.tavily.com/
- **API Reference**: https://docs.tavily.com/api-reference
- **Dashboard**: https://app.tavily.com/

### Exemplos de Integração
- [Implementação Web Search Tool](../../tools/web_search_tool.py)
- [Documentação Web Search](../../docs/WEB_SEARCH_IMPLEMENTATION.md)

### Suporte
- **Email**: support@tavily.com
- **Discord**: https://discord.gg/tavily
- **GitHub Issues**: https://github.com/tavily-ai/tavily-python

---

## ✅ Checklist de Configuração

- [ ] Conta criada no Tavily
- [ ] API key obtida
- [ ] `TAVILY_API_KEY` configurada no `.env`
- [ ] Aplicação reiniciada
- [ ] Agente com `web_search` criado
- [ ] Teste de busca realizado
- [ ] Monitoramento de quota configurado

---

**Última atualização**: 2025-11-12  
**Versão**: 1.0.0

