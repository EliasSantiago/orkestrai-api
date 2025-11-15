# 🔌 MCP (Model Context Protocol) Setup Guide

Este guia explica como configurar e usar o MCP (Model Context Protocol) no seu projeto, permitindo que seus agentes usem ferramentas externas como o Notion.

## 📋 Índice

- [O que é MCP?](#o-que-é-mcp)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Configuração do Notion](#configuração-do-notion)
- [Usando Ferramentas MCP nos Agentes](#usando-ferramentas-mcp-nos-agentes)
- [Ferramentas Disponíveis](#ferramentas-disponíveis)
- [Troubleshooting](#troubleshooting)

## 🎯 O que é MCP?

O Model Context Protocol (MCP) é um protocolo que permite que agentes de IA interajam com ferramentas e serviços externos de forma padronizada. No nosso projeto, implementamos uma camada MCP que permite:

- Conectar-se a servidores MCP (como Notion)
- Expor ferramentas MCP como ferramentas que agentes podem usar
- Gerenciar múltiplas conexões MCP de forma centralizada

## 📁 Estrutura do Projeto

A camada MCP está organizada da seguinte forma:

```
src/
├── mcp/
│   ├── __init__.py          # Módulo MCP principal
│   ├── client.py            # Cliente MCP base e gerenciador
│   ├── init.py              # Inicialização dos clientes MCP
│   └── notion/               # Integração específica do Notion
│       ├── __init__.py
│       └── client.py         # Cliente Notion MCP
│
tools/
└── mcp/                      # Ferramentas wrapper para agentes
    ├── __init__.py
    └── notion_tools.py      # Ferramentas Notion expostas aos agentes
```

### Componentes Principais

1. **`src/mcp/client.py`**: Classe base `MCPClient` e `MCPManager` para gerenciar conexões
2. **`src/mcp/notion/client.py`**: Implementação específica do cliente Notion
3. **`tools/mcp/notion_tools.py`**: Funções wrapper que expõem ferramentas Notion aos agentes
4. **`src/mcp/init.py`**: Inicialização automática dos clientes MCP no startup da aplicação

## 🔧 Configuração do Notion

### ⚠️ IMPORTANTE: Sistema Atualizado para MCP Oficial

O sistema agora usa o **MCP oficial do Notion**, que requer autenticação via **OAuth access token**. 

**📖 Para instruções detalhadas, consulte:** [`NOTION_CONNECTION_GUIDE.md`](./NOTION_CONNECTION_GUIDE.md)

### Resumo Rápido:

#### Opção 1: Via App Notion (Recomendado)
1. Abra o app Notion
2. Vá em Settings → Connections → Notion MCP
3. Conecte sua ferramenta e copie o token

#### Opção 2: Via Notion Developers (Alternativa)
1. Acesse https://www.notion.so/my-integrations
2. Crie uma nova integração
3. Copie o **Internal Integration Token** (começa com `secret_`)
4. Conecte a integração às páginas que você quer acessar

### Conectar via API:

```bash
curl -X POST 'http://localhost:8001/api/mcp/notion/connect' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
    "access_token": "secret_seu_token_aqui"
  }'
```

### Verificar Conexão:

```bash
# Status da conexão
curl -X GET 'http://localhost:8001/api/mcp/notion/status' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'

# Listar ferramentas disponíveis
curl -X GET 'http://localhost:8001/api/mcp/notion/tools' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'
```

## 🛠️ Usando Ferramentas MCP nos Agentes

### Via API REST

Ao criar ou atualizar um agente, você pode incluir ferramentas Notion na lista de `tools`:

```json
{
  "name": "Assistente Notion",
  "description": "Agente que ajuda a gerenciar conteúdo no Notion",
  "instruction": "Você é um assistente especializado em gerenciar conteúdo no Notion...",
  "model": "gemini-2.0-flash-exp",
  "tools": [
    "notion_read_page",
    "notion_search_pages",
    "notion_create_page",
    "notion_update_page"
  ]
}
```

### Ferramentas Disponíveis

Todas as ferramentas Notion começam com `notion_`:

- `notion_read_page` - Ler uma página do Notion
- `notion_search_pages` - Buscar páginas no Notion
- `notion_create_page` - Criar uma nova página
- `notion_update_page` - Atualizar propriedades de uma página
- `notion_append_blocks` - Adicionar conteúdo a uma página
- `notion_get_database` - Obter informações de um banco de dados
- `notion_query_database` - Consultar um banco de dados com filtros

## 📚 Ferramentas Disponíveis

### `notion_read_page`

Lê uma página do Notion pelo ID.

**Parâmetros:**
- `page_id` (string, obrigatório): ID da página do Notion

**Exemplo de uso pelo agente:**
```
"Leia a página com ID abc123def456"
```

### `notion_search_pages`

Busca páginas no Notion.

**Parâmetros:**
- `query` (string, opcional): Termo de busca
- `database_id` (string, opcional): Filtrar por banco de dados específico

**Exemplo:**
```
"Busque páginas sobre 'reuniões'"
```

### `notion_create_page`

Cria uma nova página no Notion.

**Parâmetros:**
- `parent_id` (string, obrigatório): ID da página pai ou banco de dados
- `title` (string, obrigatório): Título da página
- `properties` (object, opcional): Propriedades da página (para bancos de dados)
- `content` (array, opcional): Blocos de conteúdo

**Exemplo:**
```
"Crie uma página chamada 'Reunião de Hoje' no banco de dados de reuniões"
```

### `notion_update_page`

Atualiza propriedades de uma página.

**Parâmetros:**
- `page_id` (string, obrigatório): ID da página
- `properties` (object, opcional): Propriedades a atualizar

**Exemplo:**
```
"Atualize o status da página para 'Concluído'"
```

### `notion_append_blocks`

Adiciona blocos de conteúdo a uma página.

**Parâmetros:**
- `page_id` (string, obrigatório): ID da página
- `blocks` (array, obrigatório): Array de blocos para adicionar

### `notion_get_database`

Obtém informações sobre um banco de dados.

**Parâmetros:**
- `database_id` (string, obrigatório): ID do banco de dados

### `notion_query_database`

Consulta um banco de dados com filtros e ordenação.

**Parâmetros:**
- `database_id` (string, obrigatório): ID do banco de dados
- `filter` (object, opcional): Critérios de filtro
- `sorts` (array, opcional): Critérios de ordenação

## 🔍 Troubleshooting

### Erro: "Notion MCP client not initialized"

**Causa:** A `NOTION_API_KEY` não está configurada ou está incorreta.

**Solução:**
1. Verifique se a variável está no arquivo `.env`
2. Reinicie a aplicação após adicionar a chave
3. Verifique se a chave começa com `secret_`

### Erro: "Notion API error: 401"

**Causa:** A chave da API está incorreta ou expirou.

**Solução:**
1. Gere uma nova chave no Notion
2. Atualize o `.env` com a nova chave
3. Reinicie a aplicação

### Erro: "Notion API error: 404"

**Causa:** A página ou banco de dados não existe ou a integração não tem acesso.

**Solução:**
1. Verifique se o ID da página/banco está correto
2. Certifique-se de que a integração tem acesso à página/banco
3. Adicione a conexão na página do Notion

### Ferramentas MCP não aparecem

**Causa:** O cliente MCP não foi inicializado corretamente.

**Solução:**
1. Verifique os logs de inicialização
2. Certifique-se de que `NOTION_API_KEY` está configurada
3. Verifique se não há erros de importação

## 🚀 Próximos Passos

1. **Adicionar mais integrações MCP**: Você pode criar novos clientes MCP seguindo o padrão do Notion
2. **Personalizar ferramentas**: Modifique `tools/mcp/notion_tools.py` para adicionar validações ou transformações
3. **Monitoramento**: Adicione logs e métricas para monitorar o uso das ferramentas MCP

## 📖 Referências

- [Notion API Documentation](https://developers.notion.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Notion Integration Setup](https://www.notion.so/help/create-integrations-with-the-notion-api)

