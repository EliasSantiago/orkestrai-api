# 🔍 Busca Web Simples - Setup Rápido

## 🚀 A forma mais fácil de adicionar busca na internet aos seus agentes

### ✅ Passo 1: Adicione a API Key no `.env`

```bash
# Adicione esta linha ao seu arquivo .env
TAVILY_API_KEY=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
```

### ✅ Passo 2: Adicione a ferramenta ao agente

Ao criar ou atualizar um agente, adicione `"tavily_web_search"` ao campo `tools`:

```json
{
  "name": "Assistente de Pesquisa",
  "description": "Agente que busca informações na internet",
  "instruction": "Use 'tavily_web_search' para buscar informações atualizadas na web...",
  "model": "gemini-2.5-flash",
  "tools": [
    "get_current_time",
    "tavily_web_search"
  ],
  "use_file_search": false
}
```

### ✅ Pronto!

O agente agora pode buscar informações na internet! Não precisa:
- ❌ Conectar manualmente ao Tavily MCP
- ❌ Fazer configuração por usuário
- ❌ Nada de burocracia

## 📋 Exemplo Completo

```json
{
  "name": "Assistente de Pesquisa Web",
  "description": "Agente especializado em buscar informações atualizadas na internet",
  "instruction": "Você é um assistente especializado em pesquisar informações na web.\n\n**PROCESSO DE BUSCA:**\n1. Use 'get_current_time' para obter a data/hora atual\n2. Use 'tavily_web_search' para buscar informações na web\n3. Analise os resultados e forneça uma resposta clara\n4. Sempre cite as fontes (URLs)\n\nUse português brasileiro e seja preciso nas informações.",
  "model": "gemini-2.5-flash",
  "tools": [
    "get_current_time",
    "tavily_web_search"
  ],
  "use_file_search": false
}
```

## 🔧 Parâmetros da Ferramenta

```python
tavily_web_search(
    query: str,              # Query de busca (obrigatório)
    max_results: int = 5,    # Máximo de resultados (1-10, padrão: 5)
    search_depth: str = "basic"  # "basic" (rápido) ou "advanced" (mais completo)
)
```

## 📊 Resposta da Ferramenta

```json
{
  "status": "success",
  "results": [
    {
      "title": "Título do resultado",
      "url": "https://example.com",
      "content": "Conteúdo do resultado...",
      "score": 0.95
    }
  ],
  "query": "sua busca",
  "total_results": 5,
  "answer": "Resumo AI gerado (se disponível)",
  "provider": "tavily"
}
```

## ⚙️ Configuração Avançada

### Fallback para Google Custom Search

Se você não configurar `TAVILY_API_KEY`, a ferramenta tentará usar Google Custom Search como fallback (se configurado):

```bash
GOOGLE_CUSTOM_SEARCH_API_KEY=sua_chave
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=seu_engine_id
```

### Obter API Key do Tavily

1. Acesse: https://tavily.com/
2. Crie uma conta (plano gratuito disponível)
3. Obtenha sua API key no dashboard
4. Adicione ao `.env`

## 🆚 Comparação: Busca Simples vs MCP

| Característica | Busca Simples (`tavily_web_search`) | MCP (`tavily_tavily-search`) |
|----------------|--------------------------------------|------------------------------|
| Configuração | Apenas `.env` | Requer conexão manual |
| Facilidade | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Ferramentas | Apenas busca | Busca + Extract + Map + Crawl |
| Por usuário | Não (global) | Sim (cada usuário conecta) |
| Recomendado para | 90% dos casos | Casos avançados |

## ✅ Recomendação

**Use `tavily_web_search`** para a maioria dos casos. É mais simples, funciona imediatamente e não requer configuração por usuário.

Use o **MCP** apenas se precisar das ferramentas avançadas (extract, map, crawl).

