# Análise: Sistema de Ferramentas e Problema com Tool Calls

## 📋 Resumo Executivo

**Problema Reportado:** O agente ID 2 possui a ferramenta `get_current_time` configurada no banco de dados, mas ao fazer uma pergunta sobre horário ("que horas são agora em goiânia-go?"), a ferramenta não está sendo utilizada pelo modelo Gemini via Google ADK.

**Status:** ✅ Ferramentas estão sendo carregadas corretamente do banco de dados
**Status:** ⚠️ Tool calls podem não estar sendo processados corretamente pelo ADK Provider

---

## 🏗️ Arquitetura Atual

### 1. Armazenamento de Ferramentas

**Abordagem Atual:**
- ✅ **Ferramentas são salvas no banco de dados** como lista de strings (nomes das ferramentas)
- ✅ **Ferramentas são definidas em arquivos Python** em `/tools/`
- ✅ **Mapeamento nome → função** via `ToolLoaderService`

**Estrutura:**
```
/tools/
  ├── __init__.py          # Exporta: calculator, get_current_time, tavily_web_search
  ├── calculator_tool.py   # Função: calculator(expression: str) -> dict
  ├── time_tool.py         # Função: get_current_time(timezone: str) -> dict
  └── web_search_tool.py   # Função: tavily_web_search(query: str, ...) -> dict
```

**Banco de Dados:**
```sql
agents.tools = JSON  -- Exemplo: ["get_current_time", "tavily_tavily-search"]
```

### 2. Fluxo de Carregamento

```
1. Banco de Dados (agents.tools)
   ↓
2. ToolLoaderService.load_tools_for_agent()
   - Carrega ferramentas base de /tools/
   - Carrega ferramentas MCP dinâmicas
   - Retorna lista de funções Python callable
   ↓
3. ChatWithAgentUseCase.execute_stream()
   - Passa tools para provider.chat()
   ↓
4. ADKProvider.chat()
   - Recebe lista de funções
   - Cria Agent ADK com tools=adk_tools
   ↓
5. InMemoryRunner.run_async()
   - Executa agente
   - Gera eventos (texto, tool calls, etc.)
   ↓
6. ADKProvider extrai apenas texto dos eventos
   ⚠️ PROBLEMA: Tool calls não estão sendo processados!
```

---

## 🔍 Problemas Identificados

### Problema 1: Tool Calls Não Estão Sendo Processados

**Localização:** `src/core/llm_providers/adk_provider.py` (linhas 263-283)

**Código Atual:**
```python
async for event in runner.run_async(...):
    # Extract text from events
    if hasattr(event, 'content') and event.content:
        # ... extrai apenas texto ...
    
    # Also check if event has text directly
    if hasattr(event, 'text') and event.text:
        yield event.text
```

**Problema:**
- O código está extraindo apenas texto dos eventos
- Não está verificando se há tool calls nos eventos
- O Google ADK Runner deve estar gerando eventos de tool calls, mas eles não estão sendo processados

**Solução Necessária:**
- Verificar se o evento contém tool calls
- Processar tool calls automaticamente (o ADK deve fazer isso internamente)
- Garantir que os resultados das tool calls sejam incluídos na resposta

### Problema 2: Falta de Logs de Debug

**Status:** ✅ **RESOLVIDO** - Logs foram adicionados em:
- `chat_with_agent.py` (linha 321): Logs de carregamento de ferramentas
- `adk_provider.py` (linhas 102-107): Logs de ferramentas recebidas
- `adk_provider.py` (linhas 204, 212): Logs de criação do Agent ADK

### Problema 3: Verificação de Formato das Ferramentas

**Status:** ✅ **OK** - As ferramentas têm:
- ✅ Type hints corretos (`timezone: str -> dict`)
- ✅ Docstrings completas
- ✅ Formato esperado pelo Google ADK (funções Python simples)

---

## ✅ Avaliação da Abordagem Atual

### Pontos Positivos

1. **Separação de Responsabilidades:**
   - Ferramentas em `/tools/` são reutilizáveis
   - Fácil adicionar novas ferramentas
   - Código organizado e modular

2. **Flexibilidade:**
   - Ferramentas base (Python puro)
   - Ferramentas MCP (dinâmicas, por usuário)
   - Fácil extensão

3. **Manutenibilidade:**
   - Cada ferramenta em seu próprio arquivo
   - Type hints facilitam autocomplete e validação
   - Docstrings claras

### Pontos de Atenção

1. **Dependência de Nomes:**
   - Ferramentas são identificadas por nome (string)
   - Se o nome mudar, precisa atualizar banco de dados
   - **Solução:** Manter nomes estáveis ou usar IDs

2. **Validação de Ferramentas:**
   - Se uma ferramenta não existe, apenas loga warning
   - Não falha explicitamente
   - **Solução:** Adicionar validação mais rigorosa

3. **Tool Calls do ADK:**
   - O Google ADK deve processar tool calls automaticamente
   - Mas pode haver problemas na captura dos eventos
   - **Solução:** Verificar documentação do ADK sobre tool calls

---

## 🎯 Recomendações

### 1. Manter a Abordagem Atual (Recomendado)

**Por quê:**
- ✅ Arquitetura limpa e escalável
- ✅ Fácil adicionar novas ferramentas
- ✅ Separação clara entre definição e uso
- ✅ Compatível com Google ADK

**Melhorias Sugeridas:**
1. Adicionar processamento explícito de tool calls no ADK Provider
2. Adicionar validação mais rigorosa de ferramentas
3. Adicionar testes unitários para ferramentas
4. Documentar processo de adicionar novas ferramentas

### 2. Alternativa: Ferramentas como Plugins

**Abordagem:**
- Criar sistema de plugins para ferramentas
- Registrar ferramentas dinamicamente
- Suportar hot-reload

**Vantagens:**
- Mais flexível
- Permite desabilitar ferramentas sem código

**Desvantagens:**
- Mais complexo
- Overhead desnecessário para caso de uso atual

**Veredito:** Não necessário no momento

---

## 🔧 Correções Necessárias

### Correção 1: Processar Tool Calls no ADK Provider

**Arquivo:** `src/core/llm_providers/adk_provider.py`

**Ação:**
1. Verificar se eventos contêm tool calls
2. Logar quando tool calls são detectados
3. Garantir que o ADK processa tool calls automaticamente
4. Incluir resultados de tool calls na resposta

**Código Sugerido:**
```python
async for event in runner.run_async(...):
    # Log event type for debugging
    event_type = type(event).__name__
    logger.debug(f"ADK Event type: {event_type}")
    
    # Check for tool calls (ADK should handle these automatically)
    if hasattr(event, 'function_calls') or hasattr(event, 'tool_calls'):
        logger.info(f"🔧 Tool call detected in event: {event}")
    
    # Extract text from events
    # ... código existente ...
```

### Correção 2: Verificar Instruções do Agente

**Problema Potencial:**
- O agente pode não ter instruções claras sobre quando usar ferramentas
- O modelo pode não estar sendo instruído a usar `get_current_time`

**Solução:**
- Verificar se a `instruction` do agente menciona ferramentas
- Adicionar instruções explícitas sobre uso de ferramentas se necessário

### Correção 3: Testar Tool Calls Manualmente

**Ação:**
1. Criar teste simples que chama `get_current_time` diretamente
2. Verificar se a função funciona corretamente
3. Testar com Google ADK localmente
4. Verificar logs do backend durante requisição

---

## 📊 Próximos Passos

1. ✅ **Adicionar logs de debug** (CONCLUÍDO)
2. ⏳ **Verificar eventos de tool calls no ADK Provider**
3. ⏳ **Testar requisição e verificar logs**
4. ⏳ **Corrigir processamento de tool calls se necessário**
5. ⏳ **Documentar processo de adicionar novas ferramentas**

---

## 📝 Conclusão

**A abordagem atual é sólida e adequada para o caso de uso.** O problema não está na arquitetura, mas provavelmente no processamento de tool calls pelo Google ADK Provider.

**Ações Imediatas:**
1. Verificar logs do backend ao fazer requisição
2. Adicionar processamento explícito de tool calls
3. Testar com agente que tem ferramentas configuradas

**A abordagem de criar ferramentas em `/tools/` é a melhor opção** porque:
- ✅ Simples e direta
- ✅ Fácil de manter
- ✅ Compatível com Google ADK
- ✅ Escalável

