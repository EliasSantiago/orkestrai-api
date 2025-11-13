# 🔧 Guia de Ferramentas Tavily - Como Configurar Agentes

## 🎯 Problema Identificado

Você está vendo este erro nos logs:
```
Requested tools not found: ['web_search', 'time']
```

**Causa**: Os nomes das ferramentas estão **incorretos** no agente.

---

## ✅ **Ferramentas Corretas do Tavily MCP**

Como você tem o **MCP Tavily conectado** (status 200 ✅), use estas ferramentas:

| Nome da Ferramenta | Descrição | Quando Usar |
|-------------------|-----------|-------------|
| `tavily_tavily-search` | Busca web avançada com citações | Notícias, pesquisas, informações atualizadas |
| `tavily_tavily-extract` | Extração de dados de páginas | Quando tem URL específica e quer extrair dados estruturados |
| `tavily_tavily-map` | Mapeamento de estrutura de sites | Entender organização de um website |
| `tavily_tavily-crawl` | Crawling sistemático | Análise profunda de sites, múltiplas páginas |
| `get_current_time` | Hora/data atual | Contexto temporal (substitui 'time') |

---

## 🚀 **Como Corrigir Agora**

### Opção 1: Atualizar Agente Existente (Agente ID 8)

```bash
curl -X 'PUT' \
  'http://localhost:8001/api/agents/8' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwidXNlcl9pZCI6MiwiZXhwIjoxNzY1NTQ3MDM2fQ.Kx7SEQ7tVp0F9viX-u83nfSTdoDKO4q2VEJJsjcnDqI' \
  -H 'Content-Type: application/json' \
  -d '{
    "tools": [
      "get_current_time",
      "tavily_tavily-search",
      "tavily_tavily-extract"
    ]
  }'
```

### Opção 2: Criar Novo Agente com Tavily MCP

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwidXNlcl9pZCI6MiwiZXhwIjoxNzY1NTQ3MDM2fQ.Kx7SEQ7tVp0F9viX-u83nfSTdoDKO4q2VEJJsjcnDqI' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Analista de Notícias IA",
    "description": "Agente especializado em buscar e analisar notícias sobre IA usando Tavily MCP",
    "instruction": "Você é um analista de notícias especializado em Inteligência Artificial. Use tavily_tavily-search para buscar notícias recentes e relevantes. SEMPRE:\n\n1. Use get_current_time PRIMEIRO para obter data/hora atual (timezone: America/Sao_Paulo)\n2. Use tavily_tavily-search para buscar notícias com a data atual no contexto\n3. Analise os resultados e forneça um resumo claro e estruturado\n4. SEMPRE cite as fontes (URLs) dos artigos\n5. Mencione a data/hora atual na resposta\n6. Compare múltiplas fontes quando possível\n7. Responda em português brasileiro",
    "model": "gemini/gemini-2.0-flash-exp",
    "tools": [
      "get_current_time",
      "tavily_tavily-search",
      "tavily_tavily-extract"
    ],
    "use_file_search": false
  }'
```

---

## 📋 **Exemplos de Configuração por Caso de Uso**

### 1. Pesquisador de Notícias

```json
{
  "name": "Pesquisador de Notícias",
  "model": "gemini/gemini-2.0-flash-exp",
  "tools": [
    "get_current_time",
    "tavily_tavily-search"
  ]
}
```

**Uso**: Buscar notícias recentes sobre qualquer tópico.

### 2. Analista de Sites

```json
{
  "name": "Analista de Sites",
  "model": "gemini/gemini-2.0-flash-exp",
  "tools": [
    "tavily_tavily-extract",
    "tavily_tavily-map"
  ]
}
```

**Uso**: Extrair dados de sites específicos ou mapear estrutura.

### 3. Pesquisador Completo (Todas as Ferramentas)

```json
{
  "name": "Pesquisador Completo",
  "model": "gemini/gemini-2.0-flash-exp",
  "tools": [
    "get_current_time",
    "tavily_tavily-search",
    "tavily_tavily-extract",
    "tavily_tavily-map",
    "tavily_tavily-crawl"
  ]
}
```

**Uso**: Máximo poder - todas as ferramentas do Tavily MCP.

### 4. Extrator de Dados Web

```json
{
  "name": "Extrator de Dados",
  "model": "openai/gpt-4o",
  "tools": [
    "tavily_tavily-extract"
  ]
}
```

**Uso**: Apenas extração de dados de URLs específicas.

---

## 🔍 **Como Verificar Ferramentas Disponíveis**

### 1. Listar todas as ferramentas do Tavily MCP

```bash
curl -X 'GET' \
  'http://localhost:8001/api/mcp/tools/tavily' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN'
```

**Resposta esperada:**
```json
{
  "tools": [
    {
      "name": "tavily_tavily-search",
      "description": "Search the web for information"
    },
    {
      "name": "tavily_tavily-extract",
      "description": "Extract data from web pages"
    },
    {
      "name": "tavily_tavily-map",
      "description": "Create structured map of websites"
    },
    {
      "name": "tavily_tavily-crawl",
      "description": "Systematically crawl websites"
    }
  ],
  "total": 4
}
```

### 2. Verificar status do MCP

```bash
curl -X 'GET' \
  'http://localhost:8001/api/mcp/status/tavily' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN'
```

**Resposta esperada:**
```json
{
  "connected": true,
  "message": "tavily connected and working",
  "connected_at": "2025-11-10T...",
  "last_used_at": "2025-11-10T..."
}
```

---

## 📝 **Instrução de Sistema Recomendada**

Para agentes que usam Tavily MCP, use esta instrução:

```
Você é um assistente especializado em pesquisar e analisar informações da web usando as ferramentas do Tavily MCP.

**FERRAMENTAS DISPONÍVEIS:**
1. get_current_time: Obter data/hora atual
2. tavily_tavily-search: Buscar informações na web
3. tavily_tavily-extract: Extrair dados de páginas web
4. tavily_tavily-map: Mapear estrutura de websites
5. tavily_tavily-crawl: Fazer crawling de websites

**PROCESSO RECOMENDADO:**
1. PRIMEIRO: Use get_current_time para obter contexto temporal (timezone: 'America/Sao_Paulo')
2. DEPOIS: Use tavily_tavily-search para buscar informações
3. SE NECESSÁRIO: Use tavily_tavily-extract para extrair dados específicos
4. ANALISE: Combine os resultados e forneça resposta clara
5. CITE: Sempre mencione as fontes (URLs)

**SEMPRE FAZER:**
- Obter data/hora atual ANTES de buscar (para contexto)
- Citar as fontes dos resultados
- Responder em português brasileiro
- Ser claro e estruturado
```

---

## ⚠️ **Diferenças Importantes**

### ❌ Nomes Incorretos (Causam Erro)

```json
{
  "tools": [
    "web_search",     // ❌ ERRADO
    "time",           // ❌ ERRADO
    "tavily_search"   // ❌ ERRADO
  ]
}
```

### ✅ Nomes Corretos (Funcionam)

```json
{
  "tools": [
    "tavily_tavily-search",   // ✅ CORRETO
    "get_current_time",       // ✅ CORRETO
    "tavily_tavily-extract"   // ✅ CORRETO
  ]
}
```

---

## 🎯 **Resumo Rápido**

| Se você precisa de... | Use esta ferramenta |
|-----------------------|---------------------|
| Buscar notícias/informações | `tavily_tavily-search` |
| Data/hora atual | `get_current_time` |
| Extrair dados de URL | `tavily_tavily-extract` |
| Mapear estrutura de site | `tavily_tavily-map` |
| Crawling profundo | `tavily_tavily-crawl` |

---

## 🧪 **Testar Após Atualizar**

```bash
# 1. Atualizar agente (veja comandos acima)

# 2. Testar chat
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer SEU_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 8,
    "message": "Faça um resumo das principais notícias sobre IA desta semana",
    "session_id": ""
  }'
```

**Sucesso**: O agente deve usar as ferramentas do Tavily MCP sem erros ✅

---

## 📚 **Documentação Completa**

- **MCP Tavily Setup**: `docs/TAVILY_MCP_SETUP.md`
- **MCP Tavily Usage**: `docs/TAVILY_MCP_USAGE_GUIDE.md`
- **Exemplos de Agentes**: `examples/agents/`
- **Quick Start**: `docs/TAVILY_MCP_QUICK_START.md`

---

## 💡 **Dica Pro**

Para um agente completo e poderoso, use:

```json
{
  "name": "Super Pesquisador",
  "model": "gemini/gemini-2.0-flash-exp",
  "tools": [
    "get_current_time",
    "tavily_tavily-search",
    "tavily_tavily-extract",
    "tavily_tavily-map",
    "tavily_tavily-crawl"
  ],
  "instruction": "Use get_current_time ANTES de buscar. Use tavily_tavily-search para buscar. Use tavily_tavily-extract para extrair dados. SEMPRE cite fontes."
}
```

---

**Última atualização**: 2025-11-12

