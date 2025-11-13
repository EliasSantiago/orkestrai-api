# 🔍 Implementação de Busca na Internet para Agentes

> **⚠️ NOTA IMPORTANTE**: Esta documentação descreve a implementação customizada usando a API direta do Tavily. 
> 
> **✅ RECOMENDADO**: Use o [Tavily MCP oficial](./TAVILY_MCP_SETUP.md) que oferece mais ferramentas (search, extract, map, crawl) e é mantido oficialmente pela Tavily.

## 📋 Visão Geral

Esta implementação adiciona capacidade de busca na internet para os agentes de IA, permitindo que eles acessem informações atualizadas da web.

**Duas opções disponíveis:**
1. **Tavily MCP** (Recomendado) - Veja [TAVILY_MCP_SETUP.md](./TAVILY_MCP_SETUP.md)
2. **Implementação customizada** (esta documentação) - Usa API direta do Tavily

## 🎯 Abordagem Escolhida

### **Tavily Search API (Recomendado)**
- ✅ **Otimizado para agentes de IA**: Respostas estruturadas e relevantes
- ✅ **Citações automáticas**: Inclui fontes e links
- ✅ **Resumo AI**: Gera resumo inteligente dos resultados
- ✅ **Plano gratuito generoso**: 1.000 buscas/mês gratuitas
- ✅ **API simples**: Fácil de integrar
- ✅ **Rápido**: Respostas em < 2 segundos

### **Google Custom Search API (Fallback)**
- Requer configuração no Google Cloud Console
- Limite de 100 buscas/dia no plano gratuito
- Mais complexo de configurar

## 🔧 Configuração

### Opção 1: Tavily (Recomendado)

1. **Obter API Key:**
   - Acesse: https://tavily.com/
   - Crie uma conta gratuita
   - Obtenha sua API key

2. **Adicionar ao `.env`:**
   ```env
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

### Opção 2: Google Custom Search (Alternativa)

1. **Criar Custom Search Engine:**
   - Acesse: https://programmablesearchengine.google.com/
   - Crie um novo motor de busca
   - Anote o **Engine ID** (CX)

2. **Obter API Key:**
   - Acesse: https://console.cloud.google.com/
   - Ative a "Custom Search API"
   - Crie uma credencial (API Key)

3. **Adicionar ao `.env:**
   ```env
   GOOGLE_CUSTOM_SEARCH_API_KEY=your_google_api_key_here
   GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_engine_id_here
   ```

## 🚀 Como Usar

### Criar um Agente com Busca na Web

```json
{
  "name": "Assistente com Busca Web",
  "description": "Agente que pode buscar informações na internet",
  "instruction": "Você é um assistente útil que pode buscar informações atualizadas na internet. Quando o usuário perguntar sobre algo que requer informações recentes, use a ferramenta 'tavily_web_search' para buscar e depois forneça uma resposta baseada nos resultados encontrados. Sempre cite as fontes quando usar informações da busca.",
  "model": "gemini-2.5-flash",
  "tools": ["tavily_web_search", "calculator"],
  "use_file_search": false
}
```

### Exemplo de Conversa

**Usuário:** "Qual a previsão do tempo para São Paulo hoje?"

**Agente:**
1. Chama `tavily_web_search("previsão do tempo São Paulo hoje")`
2. Recebe resultados com informações atualizadas
3. Responde baseado nos resultados, citando as fontes

## 📊 Estrutura da Resposta

A ferramenta `tavily_web_search` retorna:

```json
{
  "status": "success",
  "results": [
    {
      "title": "Título do Resultado",
      "url": "https://example.com/article",
      "content": "Snippet do conteúdo...",
      "score": 0.95
    }
  ],
  "query": "sua busca",
  "total_results": 5,
  "answer": "Resumo AI gerado (apenas Tavily)",
  "provider": "tavily"
}
```

## 🏢 Melhores Práticas (Grandes Empresas)

### O que grandes empresas fazem:

1. **Perplexity AI**: Usa busca na web + LLM para gerar respostas com citações
2. **ChatGPT (Web Browsing)**: Integra busca na web diretamente no modelo
3. **Google Bard/Gemini**: Usa Google Search integrado
4. **Claude (Anthropic)**: Usa ferramentas de busca quando necessário

### Padrões comuns:

- ✅ **Citações obrigatórias**: Sempre citar fontes
- ✅ **Validação de resultados**: Verificar relevância antes de usar
- ✅ **Limite de resultados**: Usar top 5-10 resultados mais relevantes
- ✅ **Cache inteligente**: Cachear buscas frequentes
- ✅ **Rate limiting**: Limitar buscas por usuário/sessão

## 🔒 Segurança e Limites

### Limites Recomendados:
- **Por usuário**: Máximo 10 buscas por sessão
- **Por agente**: Máximo 5 buscas por resposta
- **Timeout**: 30 segundos por busca

### Boas Práticas:
- Validar queries antes de buscar
- Filtrar conteúdo sensível/inadequado
- Logar todas as buscas para auditoria
- Implementar rate limiting

## 📝 Parâmetros da Ferramenta

```python
tavily_web_search(
    query: str,              # Query de busca (obrigatório)
    max_results: int = 5,    # Máximo de resultados (1-10, padrão: 5)
    search_depth: str = "basic"  # "basic" (rápido) ou "advanced" (mais completo)
)
```

## 🎨 Exemplo de Agente Completo

```json
{
  "name": "Assistente de Pesquisa",
  "description": "Agente especializado em pesquisar e resumir informações da web",
  "instruction": "Você é um assistente de pesquisa especializado. Quando o usuário pedir informações que requerem dados atualizados, use 'tavily_web_search' para buscar. Sempre:\n1. Busque informações relevantes\n2. Analise os resultados\n3. Forneça uma resposta clara e completa\n4. Cite as fontes (URLs) dos resultados usados\n5. Se não encontrar informações suficientes, informe ao usuário",
  "model": "gemini-2.5-flash",
  "tools": ["tavily_web_search"],
  "use_file_search": false
}
```

## 🔄 Fluxo de Funcionamento

```
Usuário pergunta algo que requer busca
    ↓
Agente identifica necessidade de busca
    ↓
Chama tavily_web_search(query)
    ↓
Tavily/Google busca na web
    ↓
Retorna resultados estruturados
    ↓
Agente analisa resultados
    ↓
Gera resposta com citações
```

## ⚠️ Notas Importantes

1. **Custo**: Tavily tem plano gratuito generoso, mas monitorar uso
2. **Latência**: Buscas adicionam ~1-3 segundos à resposta
3. **Qualidade**: Resultados dependem da qualidade da query
4. **Privacidade**: Queries são enviadas para APIs externas

## 🚀 Próximos Passos

- [ ] Implementar cache de buscas frequentes
- [ ] Adicionar rate limiting por usuário
- [ ] Implementar validação de queries
- [ ] Adicionar métricas de uso

