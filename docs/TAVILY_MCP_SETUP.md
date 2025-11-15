# 🔍 Tavily MCP Integration - Setup Guide

## 📋 Visão Geral

Existem **duas formas** de usar o Tavily na aplicação:

### 1. 🚀 **Busca Web Simples (Recomendado para a maioria dos casos)**

Use a ferramenta `tavily_web_search` que funciona diretamente com a API do Tavily.

**Vantagens:**
- ✅ **Zero configuração** - apenas adicione `TAVILY_API_KEY` no `.env`
- ✅ **Funciona imediatamente** - não precisa conectar manualmente
- ✅ **Simples** - apenas adicione `"tavily_web_search"` ao campo `tools` do agente
- ✅ **Global** - todos os usuários podem usar (compartilha a API key)

**Como usar:**
1. Adicione `TAVILY_API_KEY=tvly-dev-...` no `.env`
2. Adicione `"tavily_web_search"` ao campo `tools` do agente
3. Pronto! O agente pode buscar na web

### 2. 🔧 **MCP Avançado (Para ferramentas extras)**

Use o servidor MCP remoto do Tavily para acessar ferramentas avançadas:

- **tavily-search**: Busca em tempo real na web
- **tavily-extract**: Extrai dados de páginas web
- **tavily-map**: Cria um mapa estruturado de websites
- **tavily-crawl**: Faz crawling sistemático de websites

**Vantagens:**
- ✅ **Mais ferramentas** além de busca (extract, map, crawl)
- ✅ **Implementação oficial e mantida** pela Tavily
- ✅ **Atualizações automáticas** sem necessidade de atualizar código
- ✅ **Padronizado com MCP** (Model Context Protocol)

**Desvantagens:**
- ⚠️ Requer conexão manual via `/api/mcp/connect`
- ⚠️ Cada usuário precisa conectar sua própria conta

## 🔑 Obter API Key

1. Acesse: https://tavily.com/
2. Crie uma conta (plano gratuito disponível)
3. Obtenha sua API key no dashboard

## 🔌 Conectar ao Tavily MCP

### Via API

```bash
curl -X POST 'http://localhost:8001/api/mcp/connect' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "provider": "tavily",
    "credentials": {
      "api_key": "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"
    }
  }'
```

### Resposta de Sucesso

```json
{
  "id": 1,
  "provider": "tavily",
  "is_active": true,
  "connected_at": "2025-11-10T10:00:00",
  "last_used_at": null,
  "metadata": {}
}
```

## 🛠️ Verificar Conexão

```bash
curl -X GET 'http://localhost:8001/api/mcp/status/tavily' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

## 📋 Listar Ferramentas Disponíveis

```bash
curl -X GET 'http://localhost:8001/api/mcp/tools/tavily' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

## 🤖 Criar Agente com Tavily MCP

Para usar as ferramentas do Tavily MCP, simplesmente adicione os nomes das ferramentas ao campo `tools` do agente:

```json
{
  "name": "Assistente de Pesquisa Avançada",
  "description": "Agente que usa Tavily MCP para busca, extração e análise web",
  "instruction": "Você é um assistente especializado em pesquisar e analisar informações da web usando as ferramentas do Tavily MCP.\n\n**FERRAMENTAS DISPONÍVEIS:**\n1. **tavily_tavily-search**: Use para buscar informações atualizadas na web\n2. **tavily_tavily-extract**: Use para extrair dados específicos de páginas web\n3. **tavily_tavily-map**: Use para mapear a estrutura de websites\n4. **tavily_tavily-crawl**: Use para fazer crawling sistemático de websites\n\n**PROCESSO RECOMENDADO:**\n1. Use 'get_current_time' para obter data/hora atual\n2. Use 'tavily_tavily-search' para buscar informações\n3. Se necessário, use 'tavily_tavily-extract' para extrair dados específicos\n4. Analise e apresente os resultados de forma clara\n\nSempre cite as fontes e seja preciso nas informações.",
  "model": "gemini-2.5-flash",
  "tools": [
    "get_current_time",
    "tavily_tavily-search",
    "tavily_tavily-extract"
  ],
  "use_file_search": false
}
```

**📋 Nomes das Ferramentas Tavily MCP:**
- `tavily_tavily-search` - Busca na web
- `tavily_tavily-extract` - Extrai dados de páginas web
- `tavily_tavily-map` - Mapeia estrutura de websites
- `tavily_tavily-crawl` - Faz crawling de websites

**⚠️ IMPORTANTE**: 
- Você **DEVE** estar conectado ao Tavily MCP (`/api/mcp/connect`) para que as ferramentas estejam disponíveis
- Adicione apenas as ferramentas que você quer usar no campo `tools`
- Para ver todas as ferramentas disponíveis, use: `GET /api/mcp/tools/tavily`

## 🔄 Migração da Implementação Customizada

Se você estava usando a ferramenta `tavily_web_search` customizada:

1. **Conecte ao Tavily MCP** usando o endpoint `/api/mcp/connect`
2. **Remova `tavily_web_search`** da lista de tools dos seus agentes
3. **As ferramentas do MCP serão descobertas automaticamente** e estarão disponíveis como:
   - `tavily_tavily-search` (ou apenas `tavily-search` dependendo da configuração)
   - `tavily_tavily-extract`
   - `tavily_tavily-map`
   - `tavily_tavily-crawl`

## 📚 Ferramentas Disponíveis

### tavily-search

Busca em tempo real na web com resultados estruturados e citações.

**Parâmetros:**
- `query` (string, obrigatório): Query de busca
- `max_results` (int, opcional): Número máximo de resultados (padrão: 5)
- `search_depth` (string, opcional): "basic" ou "advanced" (padrão: "basic")

### tavily-extract

Extrai dados específicos de páginas web.

**Parâmetros:**
- `url` (string, obrigatório): URL da página
- `extraction_prompt` (string, opcional): Prompt para extração

### tavily-map

Cria um mapa estruturado de um website.

**Parâmetros:**
- `url` (string, obrigatório): URL do website
- `max_depth` (int, opcional): Profundidade máxima do mapeamento

### tavily-crawl

Faz crawling sistemático de websites.

**Parâmetros:**
- `url` (string, obrigatório): URL inicial
- `max_pages` (int, opcional): Número máximo de páginas

## ⚠️ Notas Importantes

1. **API Key**: Mantenha sua API key segura. Ela é criptografada no banco de dados.
2. **Rate Limits**: Tavily tem limites de uso. Verifique seu plano em https://tavily.com/
3. **Custo**: O plano gratuito é generoso, mas monitore o uso em produção.
4. **Isolamento**: Cada usuário precisa conectar sua própria conta Tavily.

## 🔗 Referências

- [Tavily MCP GitHub](https://github.com/tavily-ai/tavily-mcp)
- [Tavily Documentation](https://docs.tavily.com/)
- [MCP Specification](https://modelcontextprotocol.io/)

