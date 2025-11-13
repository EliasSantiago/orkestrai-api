# 🤖 Guia Completo: Exemplos de Agentes para Criação

Este documento apresenta exemplos práticos e completos para criar agentes que utilizam as principais ferramentas disponíveis: **Tavily MCP** (busca web), **Google Calendar** (gerenciamento de eventos) e **RAG** (busca em documentos com gemini-2.5-flash).

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Agente com Tavily MCP](#agente-com-tavily-mcp)
3. [Agente com Google Calendar](#agente-com-google-calendar)
4. [Agente com RAG (File Search)](#agente-com-rag-file-search)
5. [Agente Híbrido (Múltiplas Ferramentas)](#agente-híbrido-múltiplas-ferramentas)
6. [Checklist de Criação](#checklist-de-criação)

---

## 🔧 Pré-requisitos

### Para Tavily MCP
1. ✅ Conectar ao Tavily MCP via API
2. ✅ Obter API key do Tavily
3. ✅ Verificar ferramentas disponíveis

### Para Google Calendar
1. ✅ Criar projeto no Google Cloud Console
2. ✅ Habilitar Google Calendar API
3. ✅ Configurar OAuth 2.0
4. ✅ Conectar conta Google Calendar via API

### Para RAG (File Search)
1. ✅ Criar File Search Store
2. ✅ Fazer upload de arquivos
3. ✅ Aguardar processamento dos arquivos

---

## 🔍 Agente com Tavily MCP

### Visão Geral

Agente especializado em pesquisar e analisar informações da web usando as ferramentas avançadas do Tavily MCP.

### Ferramentas Disponíveis

- `tavily_search` - Buscar informações na web com resultados estruturados
- `tavily_extract` - Extrair dados específicos de páginas web
- `tavily_map` - Mapear estrutura de websites
- `tavily_crawl` - Fazer crawling sistemático de websites
- `get_current_time` - Obter data/hora atual (recomendado para contexto temporal)

### Exemplo Completo de Agente

```json
{
  "name": "Assistente de Pesquisa Avançada",
  "description": "Agente que usa Tavily MCP para busca, extração e análise web com contexto temporal",
  "instruction": "Você é um assistente especializado em pesquisar e analisar informações da web usando as ferramentas do Tavily MCP.\n\n**FERRAMENTAS DISPONÍVEIS DO TAVILY MCP:**\n1. **tavily_search**: Use para buscar informações atualizadas na web com resultados estruturados e citações\n2. **tavily_extract**: Use para extrair dados específicos de páginas web\n3. **tavily_map**: Use para mapear a estrutura de websites\n4. **tavily_crawl**: Use para fazer crawling sistemático de websites\n\n**PROCESSO DE BUSCA (SEMPRE SEGUIR ESTA ORDEM):**\n1. **PRIMEIRO**: Use 'get_current_time' para obter a data e hora atual (timezone: 'America/Sao_Paulo')\n2. **DEPOIS**: Use 'tavily_search' para buscar informações na web\n3. **SE NECESSÁRIO**: Use 'tavily_extract' para extrair dados específicos de URLs encontradas\n4. **ANALISE**: Combine o contexto temporal (data/hora atual) com os resultados da busca\n5. **RESPONDA**: Forneça uma resposta clara, completa e bem estruturada, sempre mencionando a data/hora atual quando relevante\n\n**QUANDO USAR CADA FERRAMENTA:**\n- **tavily_search**: Para buscar informações gerais, notícias, previsões, dados atualizados\n- **tavily_extract**: Quando precisar extrair dados específicos de uma página web conhecida\n- **tavily_map**: Quando precisar entender a estrutura de um website\n- **tavily_crawl**: Quando precisar fazer uma análise profunda de um website\n\n**SEMPRE FAZER:**\n1. Obter data/hora atual ANTES de buscar (para contexto temporal)\n2. Usar a data/hora atual para contextualizar os resultados da busca\n3. Mencionar a data/hora atual na resposta quando relevante (ex: 'Hoje, 10 de novembro de 2025...')\n4. Analisar os resultados da busca cuidadosamente\n5. Forneça uma resposta clara, completa e bem estruturada\n6. Cite as fontes (URLs) dos resultados que você usou\n7. Combine informações de múltiplas fontes quando apropriado\n8. Se não encontrar informações suficientes ou relevantes, informe ao usuário honestamente\n9. Use português brasileiro\n\n**EXEMPLO DE FLUXO:**\nUsuário: 'Qual a previsão do tempo para hoje?'\n1. Você chama: get_current_time('America/Sao_Paulo') → obtém: '2025-11-10 14:30:00'\n2. Você chama: tavily_search(query='previsão do tempo São Paulo hoje 10 novembro 2025')\n3. Você responde: 'Hoje, 10 de novembro de 2025, às 14:30, a previsão do tempo para São Paulo é...' (com citações)",
  "model": "gemini-2.5-flash",
  "tools": [
    "get_current_time",
    "tavily_search",
    "tavily_extract"
  ],
  "use_file_search": false
}
```

### Como Criar

```bash
curl -X POST 'http://localhost:8001/api/agents' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Assistente de Pesquisa Avançada",
    "description": "Agente que usa Tavily MCP para busca, extração e análise web",
    "instruction": "Você é um assistente especializado em pesquisar informações na web...",
    "model": "gemini-2.5-flash",
    "tools": [
      "get_current_time",
      "tavily_search",
      "tavily_extract"
    ],
    "use_file_search": false
  }'
```

### Exemplos de Uso

**Busca de Informações:**
```
Usuário: "Qual a previsão do tempo para hoje em São Paulo?"

Agente: 
1. Obtém data/hora atual
2. Busca informações sobre previsão do tempo
3. Responde com informações atualizadas e citações
```

**Extração de Dados:**
```
Usuário: "Extraia os dados principais desta página: https://example.com"

Agente:
1. Usa tavily_extract para extrair dados estruturados
2. Apresenta os dados de forma organizada
```

**Mapeamento de Website:**
```
Usuário: "Mapeie a estrutura do site https://example.com"

Agente:
1. Usa tavily_map para entender a estrutura
2. Apresenta um mapa organizado do site
```

### Checklist Tavily

- [ ] Conectei ao Tavily MCP (`POST /api/mcp/connect`)
- [ ] Verifiquei status da conexão (`GET /api/mcp/status/tavily`)
- [ ] Liste as ferramentas disponíveis (`GET /api/mcp/tools/tavily`)
- [ ] Criei o agente com as ferramentas corretas
- [ ] Testei o agente com uma busca simples

---

## 📅 Agente com Google Calendar

### Visão Geral

Agente especializado em gerenciar eventos no Google Calendar. Pode criar, listar, atualizar e deletar eventos, além de gerenciar múltiplos calendários.

### Ferramentas Disponíveis

- `google_calendar_create_event` - Criar novo evento
- `google_calendar_list_events` - Listar eventos
- `google_calendar_get_event` - Obter evento específico
- `google_calendar_update_event` - Atualizar evento
- `google_calendar_delete_event` - Deletar evento
- `google_calendar_list_calendars` - Listar calendários disponíveis

### Exemplo Completo de Agente

```json
{
  "name": "Assistente de Agenda Google",
  "description": "Agente especializado em gerenciar eventos no Google Calendar. Pode criar, listar, atualizar e deletar eventos, além de gerenciar múltiplos calendários.",
  "instruction": "Você é um assistente especializado em gerenciar eventos no Google Calendar. Suas responsabilidades incluem:\n\n**Criar Eventos:**\n- Sempre pergunte: título, data/hora de início, data/hora de fim\n- Pergunte opcionalmente: localização, descrição, participantes (emails)\n- Use 'google_calendar_create_event' para criar\n- Por padrão, use 'primary' como calendar_id (calendário principal)\n\n**Listar Eventos:**\n- Use 'google_calendar_list_events' para buscar eventos\n- Você pode filtrar por período usando time_min e time_max (formato ISO 8601)\n- Use 'q' para buscar por palavras-chave\n- Pergunte ao usuário qual período ele quer ver (hoje, esta semana, este mês, etc.)\n\n**Obter Evento Específico:**\n- Use 'google_calendar_get_event' quando o usuário pedir detalhes de um evento específico\n- Você precisará do event_id (obtido ao listar eventos)\n\n**Atualizar Eventos:**\n- Use 'google_calendar_update_event' para modificar eventos existentes\n- Sempre pergunte o que o usuário quer alterar (título, horário, localização, etc.)\n- Você precisará do event_id\n\n**Deletar Eventos:**\n- Use 'google_calendar_delete_event' para remover eventos\n- Sempre confirme antes de deletar\n- Você precisará do event_id\n\n**Gerenciar Calendários:**\n- Use 'google_calendar_list_calendars' para ver todos os calendários disponíveis\n- Isso é útil quando o usuário quer criar eventos em calendários específicos\n\n**Boas Práticas:**\n- Sempre confirme informações importantes antes de criar/modificar eventos\n- Use português brasileiro\n- Seja claro e objetivo\n- Quando listar eventos, apresente de forma organizada (data, hora, título)\n- Se um evento não for encontrado, informe claramente\n- Para datas/horas, sempre pergunte se não estiver claro\n\n**Formato de Datas:**\n- Use formato ISO 8601 para datas/horas\n- Exemplo: '2024-01-15T14:00:00-03:00' (15 de janeiro de 2024, 14h, timezone -03:00)\n- Se o usuário fornecer apenas data/hora sem timezone, assuma o timezone local do Brasil (-03:00)\n\n**Exemplos de Interação:**\n- \"Crie um evento para reunião amanhã às 14h\" → Você pergunta: título completo, duração, localização\n- \"Quais eventos tenho esta semana?\" → Você lista eventos usando time_min e time_max\n- \"Mude o horário da reunião de amanhã para 15h\" → Você busca o evento, depois atualiza\n- \"Delete o evento de consulta médica\" → Você busca o evento, confirma e deleta",
  "model": "gpt-4o-mini",
  "tools": [
    "google_calendar_create_event",
    "google_calendar_list_events",
    "google_calendar_get_event",
    "google_calendar_update_event",
    "google_calendar_delete_event",
    "google_calendar_list_calendars"
  ],
  "use_file_search": false
}
```

### Como Criar

```bash
curl -X POST 'http://localhost:8001/api/agents' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Assistente de Agenda Google",
    "description": "Agente especializado em gerenciar eventos no Google Calendar",
    "instruction": "Você é um assistente especializado em gerenciar eventos no Google Calendar...",
    "model": "gpt-4o-mini",
    "tools": [
      "google_calendar_create_event",
      "google_calendar_list_events",
      "google_calendar_get_event",
      "google_calendar_update_event",
      "google_calendar_delete_event",
      "google_calendar_list_calendars"
    ],
    "use_file_search": false
  }'
```

### Exemplos de Uso

**Criar Evento:**
```
Usuário: "Crie um evento para reunião de equipe amanhã às 14h"

Agente: 
1. Pergunta detalhes (título completo, duração, localização)
2. Cria o evento usando google_calendar_create_event
3. Confirma a criação
```

**Listar Eventos:**
```
Usuário: "Quais eventos tenho esta semana?"

Agente:
1. Usa google_calendar_list_events com time_min e time_max
2. Apresenta eventos de forma organizada
```

**Atualizar Evento:**
```
Usuário: "Mude o horário da reunião de amanhã para 15h"

Agente:
1. Busca o evento usando google_calendar_list_events
2. Atualiza usando google_calendar_update_event
3. Confirma a atualização
```

**Deletar Evento:**
```
Usuário: "Delete o evento de consulta médica"

Agente:
1. Busca o evento
2. Confirma antes de deletar
3. Deleta usando google_calendar_delete_event
```

### Checklist Google Calendar

- [ ] Configurei projeto no Google Cloud Console
- [ ] Habilitei Google Calendar API
- [ ] Configurei OAuth 2.0
- [ ] Conectei conta Google Calendar (`POST /api/mcp/connect`)
- [ ] Verifiquei status da conexão (`GET /api/mcp/status/google_calendar`)
- [ ] Liste as ferramentas disponíveis (`GET /api/mcp/tools/google_calendar`)
- [ ] Criei o agente com todas as ferramentas
- [ ] Testei criando um evento
- [ ] Testei listando eventos

---

## 📚 Agente com RAG (File Search)

### Visão Geral

Agente especializado em responder perguntas baseado nos documentos enviados. Usa RAG (Retrieval-Augmented Generation) para buscar informações relevantes nos arquivos e fornecer respostas precisas e contextualizadas.

### Características Importantes

- ✅ **Automático**: RAG é adicionado automaticamente quando `use_file_search: true`
- ✅ **Modelo Gemini**: Funciona apenas com modelos Gemini (recomendado: `gemini-2.5-flash`)
- ✅ **File Search Stores**: Usa apenas stores ativos (`is_active: true`)
- ✅ **Segurança**: Por padrão, `use_file_search: false` (opt-out)

### Exemplo Completo de Agente

```json
{
  "name": "Assistente com RAG",
  "description": "Agente especializado em responder perguntas baseado nos documentos enviados. Usa RAG (Retrieval-Augmented Generation) para buscar informações relevantes nos seus arquivos e fornecer respostas precisas e contextualizadas.",
  "instruction": "Você é um assistente especializado em responder perguntas baseado nos documentos fornecidos pelo usuário. Suas responsabilidades incluem:\n\n**Buscar Informações nos Documentos:**\n- Use o File Search automaticamente quando o usuário fizer perguntas sobre os documentos\n- Busque informações relevantes nos arquivos enviados\n- Sempre cite a fonte quando usar informações dos documentos\n- Se não encontrar informação relevante, informe claramente\n\n**Responder Perguntas:**\n- Responda de forma clara, objetiva e precisa\n- Use português brasileiro\n- Se a informação estiver nos documentos, use-a para responder\n- Se não estiver, seja honesto e informe que não encontrou\n\n**Boas Práticas:**\n- Sempre cite a fonte quando usar informações dos documentos\n- Se encontrar múltiplas informações relevantes, organize-as de forma clara\n- Se o usuário perguntar algo que não está nos documentos, informe educadamente\n- Seja preciso e evite inventar informações\n- Quando citar informações dos documentos, mencione de qual documento veio (se disponível)\n\n**Exemplos de Interação:**\n- \"O que diz o documento sobre inteligência artificial?\" → Você busca nos documentos e responde baseado no conteúdo encontrado\n- \"Resuma os principais pontos do documento\" → Você busca e resume as informações principais\n- \"Quais são as políticas mencionadas nos documentos?\" → Você busca e lista as políticas encontradas\n- \"Explique o conceito X baseado nos documentos\" → Você busca informações sobre X e explica usando o conteúdo dos documentos\n\n**Importante:**\n- O File Search é usado automaticamente - você não precisa chamar manualmente\n- Sempre verifique se a informação está realmente nos documentos antes de responder\n- Se não tiver certeza, informe que não encontrou informação suficiente\n- Seja transparente sobre as limitações das informações disponíveis",
  "model": "gemini-2.5-flash",
  "tools": [],
  "use_file_search": true
}
```

### Como Criar

```bash
curl -X POST 'http://localhost:8001/api/agents' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Assistente com RAG",
    "description": "Agente que responde perguntas baseado nos documentos enviados",
    "instruction": "Você é um assistente especializado em responder perguntas baseado nos documentos fornecidos...",
    "model": "gemini-2.5-flash",
    "tools": [],
    "use_file_search": true
  }'
```

### Exemplos de Uso

**Pergunta sobre Documentos:**
```
Usuário: "O que diz o documento sobre inteligência artificial?"

Agente:
1. Busca automaticamente nos documentos usando File Search
2. Encontra informações relevantes
3. Responde baseado no conteúdo encontrado
4. Cita a fonte quando apropriado
```

**Resumo de Documentos:**
```
Usuário: "Resuma os principais pontos do documento"

Agente:
1. Busca e analisa os documentos
2. Resume as informações principais
3. Organiza de forma clara
```

**Busca de Políticas:**
```
Usuário: "Quais são as políticas mencionadas nos documentos?"

Agente:
1. Busca por políticas nos documentos
2. Lista todas as políticas encontradas
3. Cita as fontes
```

### Checklist RAG

- [ ] Criei File Search Store (`POST /api/file-search/stores`)
- [ ] Fiz upload de arquivos (`POST /api/file-search/stores/{id}/files`)
- [ ] Aguardei processamento dos arquivos (status: `completed`)
- [ ] Criei agente com `model: "gemini-2.5-flash"`
- [ ] Configurei `use_file_search: true`
- [ ] Testei o agente com perguntas sobre os documentos

---

## 🔀 Agente Híbrido (Múltiplas Ferramentas)

### Visão Geral

Agente que combina múltiplas ferramentas para oferecer funcionalidades completas: busca web (Tavily), gerenciamento de calendário (Google Calendar) e busca em documentos (RAG).

### Exemplo Completo de Agente Híbrido

```json
{
  "name": "Assistente Completo Multifuncional",
  "description": "Agente versátil que combina busca web (Tavily), gerenciamento de calendário (Google Calendar) e busca em documentos (RAG)",
  "instruction": "Você é um assistente completo e versátil que pode ajudar com diversas tarefas:\n\n**BUSCA WEB (Tavily):**\n- Use 'get_current_time' para obter data/hora atual antes de buscar\n- Use 'tavily_search' para buscar informações atualizadas na web\n- Use 'tavily_extract' para extrair dados de páginas específicas\n- Sempre cite as fontes e mencione a data/hora quando relevante\n\n**GERENCIAMENTO DE CALENDÁRIO (Google Calendar):**\n- Use 'google_calendar_create_event' para criar eventos\n- Use 'google_calendar_list_events' para listar eventos\n- Use 'google_calendar_update_event' para atualizar eventos\n- Use 'google_calendar_delete_event' para deletar eventos (sempre confirme antes)\n- Use 'google_calendar_list_calendars' para ver calendários disponíveis\n- Sempre pergunte detalhes antes de criar/modificar eventos\n\n**BUSCA EM DOCUMENTOS (RAG):**\n- O File Search é usado automaticamente quando você precisa buscar informações nos documentos do usuário\n- Sempre cite a fonte quando usar informações dos documentos\n- Se não encontrar informação nos documentos, informe claramente\n\n**PROCESSO DE DECISÃO:**\n1. Se o usuário pedir informações atualizadas da web → Use Tavily\n2. Se o usuário pedir para gerenciar eventos → Use Google Calendar\n3. Se o usuário perguntar sobre documentos enviados → Use RAG (automático)\n4. Se não tiver certeza, pergunte ao usuário qual ferramenta usar\n\n**BOAS PRÁTICAS:**\n- Use português brasileiro\n- Seja claro e objetivo\n- Sempre confirme ações importantes (criar/deletar eventos)\n- Cite fontes quando usar informações externas\n- Seja honesto quando não encontrar informações\n- Combine informações de múltiplas fontes quando apropriado",
  "model": "gemini-2.5-flash",
  "tools": [
    "get_current_time",
    "tavily_search",
    "tavily_extract",
    "google_calendar_create_event",
    "google_calendar_list_events",
    "google_calendar_get_event",
    "google_calendar_update_event",
    "google_calendar_delete_event",
    "google_calendar_list_calendars"
  ],
  "use_file_search": true
}
```

### Como Criar

```bash
curl -X POST 'http://localhost:8001/api/agents' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Assistente Completo Multifuncional",
    "description": "Agente versátil com Tavily, Google Calendar e RAG",
    "instruction": "Você é um assistente completo e versátil...",
    "model": "gemini-2.5-flash",
    "tools": [
      "get_current_time",
      "tavily_search",
      "tavily_extract",
      "google_calendar_create_event",
      "google_calendar_list_events",
      "google_calendar_get_event",
      "google_calendar_update_event",
      "google_calendar_delete_event",
      "google_calendar_list_calendars"
    ],
    "use_file_search": true
  }'
```

### Exemplos de Uso

**Busca Web + Calendário:**
```
Usuário: "Busque informações sobre a conferência de IA e crie um evento para amanhã às 14h"

Agente:
1. Busca informações sobre a conferência usando Tavily
2. Pergunta detalhes do evento
3. Cria evento no Google Calendar
```

**RAG + Calendário:**
```
Usuário: "Baseado no documento sobre políticas, crie um evento de reunião para revisar as políticas"

Agente:
1. Busca informações sobre políticas nos documentos (RAG)
2. Pergunta detalhes do evento
3. Cria evento no Google Calendar
```

**Busca Web + RAG:**
```
Usuário: "Compare as informações sobre IA no documento com as últimas notícias"

Agente:
1. Busca informações nos documentos (RAG)
2. Busca notícias atualizadas na web (Tavily)
3. Compara e apresenta diferenças
```

---

## ✅ Checklist de Criação

### Checklist Geral

- [ ] Tenho token JWT válido
- [ ] Endpoint da API está acessível
- [ ] Entendo a estrutura do payload JSON

### Checklist por Tipo de Agente

#### Para Agente Tavily:
- [ ] Conectei ao Tavily MCP
- [ ] Verifiquei status da conexão
- [ ] Liste as ferramentas disponíveis
- [ ] Criei agente com ferramentas corretas
- [ ] Testei com busca simples

#### Para Agente Google Calendar:
- [ ] Configurei Google Cloud Console
- [ ] Habilitei Google Calendar API
- [ ] Configurei OAuth 2.0
- [ ] Conectei conta Google Calendar
- [ ] Verifiquei status da conexão
- [ ] Liste as ferramentas disponíveis
- [ ] Criei agente com todas as ferramentas
- [ ] Testei criando evento

#### Para Agente RAG:
- [ ] Criei File Search Store
- [ ] Fiz upload de arquivos
- [ ] Aguardei processamento
- [ ] Criei agente com `gemini-2.5-flash`
- [ ] Configurei `use_file_search: true`
- [ ] Testei com perguntas sobre documentos

---

## 📝 Estrutura do Payload

### Campos Obrigatórios

- `name` (string) - Nome do agente
- `instruction` (string) - Instruções detalhadas (system prompt)

### Campos Opcionais

- `description` (string) - Descrição breve do agente
- `model` (string) - Modelo LLM (padrão: `gemini-2.0-flash-exp`)
  - Recomendado para RAG: `gemini-2.5-flash`
  - Recomendado para Google Calendar: `gpt-4o-mini`
- `tools` (array de strings) - Lista de ferramentas disponíveis
- `use_file_search` (boolean) - Habilitar RAG (padrão: `false`)

### Exemplo Mínimo

```json
{
  "name": "Meu Agente",
  "instruction": "Você é um assistente útil."
}
```

### Exemplo Completo

```json
{
  "name": "Meu Agente Completo",
  "description": "Descrição do agente",
  "instruction": "Instruções detalhadas...",
  "model": "gemini-2.5-flash",
  "tools": ["get_current_time", "tavily_search"],
  "use_file_search": true
}
```

---

## 🚀 Como Usar os Agentes

### Criar Agente

```bash
curl -X POST 'http://localhost:8001/api/agents' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d @agente.json
```

### Conversar com Agente

```bash
curl -X POST 'http://localhost:8001/api/agents/chat' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": 1,
    "message": "Sua mensagem aqui",
    "session_id": "sua-session-id"
  }'
```

### Atualizar Agente

```bash
curl -X PUT 'http://localhost:8001/api/agents/1' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "use_file_search": true
  }'
```

---

## 📚 Referências

- [Guia de Criação de Agentes](./AGENT_CREATION_GUIDE.md)
- [Tavily MCP Quick Start](./TAVILY_MCP_QUICK_START.md)
- [Google Calendar Setup](./GOOGLE_CALENDAR_SETUP.md)
- [RAG Example](./AGENT_RAG_EXAMPLE.md)
- [RAG Control](./AGENT_RAG_CONTROL.md)

---

## 💡 Dicas Finais

1. **Instruções Detalhadas**: Quanto mais detalhadas as instruções, melhor o desempenho do agente
2. **Teste Incremental**: Comece com poucas ferramentas e adicione mais conforme necessário
3. **Modelo Adequado**: Use `gemini-2.5-flash` para RAG e tarefas gerais, `gpt-4o-mini` para Google Calendar
4. **Segurança**: Por padrão, `use_file_search: false` - habilite apenas quando necessário
5. **Citações**: Sempre instrua o agente a citar fontes quando usar informações externas
6. **Confirmações**: Para ações destrutivas (deletar eventos), sempre confirme antes

---

**Pronto para criar seus agentes! 🎉**

