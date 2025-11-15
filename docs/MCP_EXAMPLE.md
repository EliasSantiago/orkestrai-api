# 📝 Exemplo de Uso: Agente com Notion MCP

Este documento mostra um exemplo prático de como criar e usar um agente que interage com o Notion através do MCP.

## 🎯 Objetivo

Criar um agente que pode:
- Buscar informações no Notion
- Criar novas páginas
- Atualizar páginas existentes
- Consultar bancos de dados

## 📋 Pré-requisitos

1. **Notion API Key configurada** (veja [MCP_SETUP.md](MCP_SETUP.md))
2. **Acesso a páginas/bancos de dados no Notion** concedido à integração

## 🚀 Passo a Passo

### 1. Configurar Notion API Key

Adicione no seu `.env`:

```bash
NOTION_API_KEY=secret_seu_token_aqui
```

### 2. Criar um Agente via API

Use a API REST para criar um agente com ferramentas Notion:

```bash
curl -X POST "http://localhost:8001/api/agents" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente Notion",
    "description": "Agente especializado em gerenciar conteúdo no Notion",
    "instruction": "Você é um assistente especializado em trabalhar com Notion. Você pode ler páginas, buscar conteúdo, criar novas páginas e atualizar informações existentes. Sempre seja claro e organizado ao criar ou atualizar conteúdo.",
    "model": "gemini-2.0-flash-exp",
    "tools": [
      "notion_read_page",
      "notion_search_pages",
      "notion_create_page",
      "notion_update_page",
      "notion_get_database",
      "notion_query_database"
    ]
  }'
```

### 3. Exemplos de Uso

#### Exemplo 1: Buscar Páginas

```bash
curl -X POST "http://localhost:8001/api/agents/chat" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "message": "Busque todas as páginas que mencionam 'reunião' no Notion"
  }'
```

O agente usará `notion_search_pages` para buscar e retornar os resultados.

#### Exemplo 2: Criar uma Nova Página

```bash
curl -X POST "http://localhost:8001/api/agents/chat" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "message": "Crie uma nova página chamada 'Reunião de Hoje' no banco de dados de reuniões. O ID do banco é abc123def456"
  }'
```

O agente usará `notion_create_page` para criar a página.

#### Exemplo 3: Ler uma Página

```bash
curl -X POST "http://localhost:8001/api/agents/chat" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "message": "Leia a página com ID xyz789abc123 e me diga o título e o conteúdo principal"
  }'
```

O agente usará `notion_read_page` para ler e resumir a página.

#### Exemplo 4: Consultar um Banco de Dados

```bash
curl -X POST "http://localhost:8001/api/agents/chat" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "message": "Consulte o banco de dados de tarefas (ID: db123) e me mostre todas as tarefas com status 'Pendente'"
  }'
```

O agente usará `notion_query_database` para consultar e filtrar.

## 💡 Dicas de Uso

### 1. IDs de Páginas e Bancos de Dados

Para obter o ID de uma página ou banco de dados no Notion:
1. Abra a página/banco no Notion
2. Copie o link (URL)
3. O ID é a parte após o último `/` e antes do `?`
   - Exemplo: `https://www.notion.so/Minha-Pagina-abc123def456ghi789`
   - ID: `abc123def456ghi789`

### 2. Instruções do Agente

Seja específico nas instruções do agente sobre como usar o Notion:

```json
{
  "instruction": "Você é um assistente especializado em Notion. Quando o usuário pedir para criar uma página, sempre pergunte o ID do banco de dados ou página pai se não for fornecido. Ao buscar páginas, seja específico e organize os resultados de forma clara. Ao criar páginas, use títulos descritivos e organize o conteúdo de forma estruturada."
}
```

### 3. Tratamento de Erros

O agente automaticamente trata erros das ferramentas MCP e informa ao usuário de forma clara. Se houver problemas de acesso ou IDs incorretos, o agente explicará o que aconteceu.

## 🔍 Verificando se Funcionou

1. **Verifique os logs da aplicação** ao iniciar:
   ```
   INFO: Connected to Notion API successfully
   INFO: Notion MCP client initialized successfully
   ```

2. **Teste uma busca simples** primeiro:
   ```
   "Busque páginas no Notion"
   ```

3. **Verifique no Notion** se as páginas foram criadas/atualizadas corretamente.

## 🎨 Casos de Uso Avançados

### Agente de Documentação

Crie um agente que automaticamente documenta reuniões:

```json
{
  "name": "Documentador de Reuniões",
  "instruction": "Você cria páginas de documentação de reuniões no Notion. Quando receber um resumo de reunião, crie uma página estruturada com: título, data, participantes, pontos principais e ações.",
  "tools": ["notion_create_page", "notion_append_blocks"]
}
```

### Agente de Busca e Análise

Crie um agente que busca e analisa conteúdo:

```json
{
  "name": "Analista de Conteúdo",
  "instruction": "Você busca e analisa conteúdo no Notion. Quando solicitado, busque páginas relevantes, leia o conteúdo e forneça análises, resumos ou insights.",
  "tools": ["notion_search_pages", "notion_read_page", "notion_query_database"]
}
```

## 📚 Próximos Passos

- Explore outras ferramentas MCP disponíveis
- Crie agentes especializados para diferentes tarefas
- Integre com outros serviços através do MCP

Veja [MCP_SETUP.md](MCP_SETUP.md) para mais detalhes sobre configuração e troubleshooting.

