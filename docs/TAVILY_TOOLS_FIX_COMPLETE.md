# 🔧 Correção Completa dos Nomes de Ferramentas Tavily

## 🐛 Problema Identificado

O sistema estava criando nomes de ferramentas com prefixo duplicado:
- ❌ `tavily_tavily-search` (errado)
- ❌ `tavily_tavily-extract` (errado)

Isso acontecia porque:
1. O servidor MCP do Tavily retorna nomes como `tavily-search`, `tavily-extract`
2. O código Python adicionava o prefixo do provider (`tavily_`)
3. Resultado: `tavily_` + `tavily-search` = `tavily_tavily-search`

## ✅ Solução Implementada

Corrigido o código em `tools/mcp/dynamic_tools.py` para:
1. Detectar se o nome da ferramenta já começa com o nome do provider
2. Remover o prefixo duplicado
3. Normalizar hífens para underscores
4. Resultado: ✅ `tavily_search`, `tavily_extract`, etc.

### Arquivos Modificados

1. **`tools/mcp/dynamic_tools.py`**
   - Função `create_dynamic_mcp_tool()` - linha ~347
   - Função `get_all_mcp_tools()` - linha ~495

2. **`docs/01_AGENTES_EXEMPLOS_COMPLETOS.md`**
   - Atualizado todos os exemplos com nomes corretos

3. **Scripts criados:**
   - `update_agent_5_tools.sh` - Script para atualizar agente 5
   - `clear_mcp_tools_cache.py` - Script para limpar cache

## 🚀 Como Aplicar a Correção

### Passo 1: Reiniciar o Backend

No terminal onde o backend está rodando:

```bash
# Pressione Ctrl+C para parar o servidor
# Depois reinicie:
./scripts/start_backend.sh
```

### Passo 2: (Opcional) Limpar Cache

Se quiser forçar o recarregamento das ferramentas:

```bash
cd /home/vdilinux/aplicações/api-adk-google-main
source .venv/bin/activate
python3 clear_mcp_tools_cache.py
```

### Passo 3: Testar

Use o mesmo cURL que estava dando erro:

```bash
curl -X 'POST' \
  'http://localhost:8001/api/agents/chat' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer SEU_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 5,
    "message": "Pesquise na internet sobre Elias Fonseca Santiago?",
    "session_id": "f88381f9-a28f-4029-886c-15425ec4745a"
  }'
```

## 📊 Resultado Esperado

### Antes (❌ Erro):
```
Agent 5 requested tools not found: ['tavily_search', 'tavily_extract']
```

### Depois (✅ Sucesso):
```
INFO: Loaded X tools from tavily MCP for user Y
INFO: Created tool wrapper: tavily_search (original: tavily-search)
INFO: Created tool wrapper: tavily_extract (original: tavily-extract)
INFO: Loaded 2 tavily tools for user Y: ['tavily_search', 'tavily_extract']
```

## 🔍 Como Verificar se Funcionou

Após reiniciar o backend, observe os logs. Você deve ver:

```
INFO: Created tool wrapper: tavily_search (original: tavily-search)
INFO: Created tool wrapper: tavily_extract (original: tavily-extract)
INFO: Created tool wrapper: tavily_map (original: tavily-map)
INFO: Created tool wrapper: tavily_crawl (original: tavily-crawl)
```

E **NÃO** deve mais ver:
```
Agent 5 requested tools not found: ['tavily_search', 'tavily_extract']
```

## 📝 Mapeamento Completo de Nomes

| MCP Server | Python Code | Descrição |
|------------|-------------|-----------|
| `tavily-search` | `tavily_search` | Busca na web |
| `tavily-extract` | `tavily_extract` | Extração de dados |
| `tavily-map` | `tavily_map` | Mapear websites |
| `tavily-crawl` | `tavily_crawl` | Crawling sistemático |

## 🎯 Lógica de Conversão

```python
# Se o nome começa com "provider-"
"tavily-search" → "tavily_search"

# Se o nome já tem "provider_"
"tavily_search" → "tavily_search" (sem mudanças)

# Se o nome não tem prefixo
"search" → "tavily_search"

# Todos os hífens são convertidos para underscores
"tavily-web-search" → "tavily_web_search"
```

## ⚠️ Importante

1. **Reiniciar é obrigatório**: As mudanças no código Python só terão efeito após reiniciar o backend
2. **Cache**: O cache de ferramentas é limpo automaticamente ao reiniciar, mas você pode limpar manualmente com o script
3. **Outros agentes**: Se você tem outros agentes usando Tavily, eles também se beneficiarão automaticamente desta correção

## ✅ Checklist de Verificação

- [x] Código corrigido em `tools/mcp/dynamic_tools.py`
- [x] Documentação atualizada em `docs/01_AGENTES_EXEMPLOS_COMPLETOS.md`
- [ ] Backend reiniciado
- [ ] Teste com cURL executado com sucesso
- [ ] Logs mostram nomes corretos das ferramentas
- [ ] Agente 5 responde sem erros

## 🆘 Troubleshooting

### Erro persiste após reiniciar

1. Verifique se o backend foi realmente reiniciado:
   ```bash
   ps aux | grep uvicorn
   ```

2. Limpe o cache manualmente:
   ```bash
   python3 clear_mcp_tools_cache.py
   ```

3. Verifique os logs do backend ao iniciar para ver se as ferramentas estão sendo carregadas corretamente

### Ferramentas ainda não são encontradas

1. Verifique se o Tavily MCP está conectado:
   ```bash
   curl -X GET 'http://localhost:8001/api/mcp/status/tavily' \
     -H 'Authorization: Bearer SEU_TOKEN'
   ```

2. Liste as ferramentas disponíveis:
   ```bash
   curl -X GET 'http://localhost:8001/api/mcp/tools/tavily' \
     -H 'Authorization: Bearer SEU_TOKEN'
   ```

3. Verifique o agente 5:
   ```bash
   curl -X GET 'http://localhost:8001/api/agents/5' \
     -H 'Authorization: Bearer SEU_TOKEN'
   ```

---

**Data da correção:** 10 de novembro de 2025
**Status:** ✅ Correção implementada, aguardando teste

