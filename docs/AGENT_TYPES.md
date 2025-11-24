# Agent Types - Google ADK Support

Este documento descreve os diferentes tipos de agentes suportados pela API OrkestrAI, baseados no Google ADK (Agent Development Kit).

## Tipos de Agentes Suportados

### 1. LLM Agent (Padrão)
Agente baseado em LLM com ferramentas (tools) e opcional RAG (File Search).

**Características:**
- Utiliza um modelo de linguagem (LLM)
- Pode ter acesso a ferramentas (tools)
- Suporta File Search (RAG) apenas com modelos Gemini 2.5 Flash
- É o tipo mais comum e versátil

**Exemplo de Criação:**
```json
POST /api/agents
{
  "name": "Analista de Notícias IA",
  "description": "Agente especializado em buscar e analisar notícias sobre IA",
  "agent_type": "llm",
  "instruction": "Você é um analista de notícias especializado em IA...",
  "model": "gemini/gemini-2.0-flash-exp",
  "tools": [
    "get_current_time",
    "tavily_tavily-search",
    "tavily_tavily-extract"
  ],
  "use_file_search": false,
  "is_favorite": false
}
```

**Exemplo com RAG (File Search):**
```json
{
  "name": "Assistente com RAG",
  "description": "Assistente que busca informações em documentos",
  "agent_type": "llm",
  "instruction": "Você é um assistente que pode buscar informações em documentos...",
  "model": "gemini/gemini-2.5-flash",
  "tools": [],
  "use_file_search": true,
  "is_favorite": false
}
```

---

### 2. Sequential Workflow Agent
Agente de workflow que executa outros agentes em sequência (um após o outro).

**Características:**
- Executa agentes em ordem sequencial
- A saída de um agente alimenta o próximo
- Útil para pipelines de processamento
- Requer pelo menos 2 agentes na sequência

**Exemplo de Criação:**
```json
POST /api/agents
{
  "name": "Pipeline de Pesquisa e Análise",
  "description": "Workflow sequencial: Pesquisa → Análise → Resumo",
  "agent_type": "sequential",
  "workflow_config": {
    "agents": [
      "pesquisador_web",
      "analisador_dados",
      "gerador_resumo"
    ],
    "description": "Executa agentes em sequência: primeiro pesquisa, depois analisa e por fim gera resumo"
  },
  "is_favorite": false
}
```

**Campos workflow_config:**
- `agents` (obrigatório): Lista de nomes/IDs dos agentes a serem executados em sequência
- `description` (opcional): Descrição do workflow

---

### 3. Loop Workflow Agent
Agente de workflow que executa um agente repetidamente até uma condição ser satisfeita.

**Características:**
- Executa o mesmo agente em loop
- Continua até que uma condição seja satisfeita
- Tem limite máximo de iterações para segurança
- Útil para processos iterativos de refinamento

**Exemplo de Criação:**
```json
POST /api/agents
{
  "name": "Revisor Iterativo",
  "description": "Loop: Revisa texto até atingir qualidade desejada",
  "agent_type": "loop",
  "workflow_config": {
    "agent": "editor_texto",
    "condition": "quality_score >= 0.9",
    "max_iterations": 5,
    "description": "Executa o editor_texto em loop até qualidade ≥ 0.9 ou 5 iterações"
  },
  "is_favorite": false
}
```

**Campos workflow_config:**
- `agent` (obrigatório): Nome/ID do agente a ser executado em loop
- `condition` (opcional): Condição de parada (expressão)
- `max_iterations` (recomendado): Número máximo de iterações
- `description` (opcional): Descrição do workflow

---

### 4. Parallel Workflow Agent
Agente de workflow que executa múltiplos agentes em paralelo.

**Características:**
- Executa vários agentes simultaneamente
- Combina os resultados de todos os agentes
- Mais rápido que execução sequencial
- Útil para análises multi-perspectiva
- Requer pelo menos 2 agentes

**Exemplo de Criação:**
```json
POST /api/agents
{
  "name": "Análise Paralela Multi-Fonte",
  "description": "Parallel: Analisa múltiplas fontes simultaneamente",
  "agent_type": "parallel",
  "workflow_config": {
    "agents": [
      "analisador_noticias",
      "analisador_redes_sociais",
      "analisador_academico"
    ],
    "description": "Executa múltiplos agentes em paralelo e retorna os resultados de todos"
  },
  "is_favorite": false
}
```

**Campos workflow_config:**
- `agents` (obrigatório): Lista de nomes/IDs dos agentes a serem executados em paralelo (mínimo 2)
- `description` (opcional): Descrição do workflow

**Nota:** Os resultados dos agentes paralelos são retornados como uma lista. A API não implementa merge automático - a combinação dos resultados deve ser feita pela aplicação cliente conforme sua necessidade.

---

### 5. Custom Agent
Agente personalizado com lógica definida pelo usuário.

**Características:**
- Permite código customizado
- Flexibilidade total na implementação
- Suporta múltiplas linguagens de runtime
- Útil para lógica de negócio específica

**Exemplo de Criação:**
```json
POST /api/agents
{
  "name": "Processador de Dados Customizado",
  "description": "Agente custom com lógica personalizada em Python",
  "agent_type": "custom",
  "custom_config": {
    "runtime": "python",
    "entry_point": "process",
    "code": "def process(context):\n    data = context.get('input')\n    result = transform_data(data)\n    return {'output': result}",
    "description": "Processa dados com lógica específica do usuário"
  },
  "is_favorite": false
}
```

**Campos custom_config:**
- `runtime` (obrigatório): Linguagem/runtime ("python", "javascript", "bash")
- `entry_point` (obrigatório): Nome da função/método de entrada
- `code` (obrigatório): Código fonte do agente
- `description` (opcional): Descrição da lógica customizada

---

## Atualização de Agentes

Todos os tipos de agentes podem ser atualizados via `PUT /api/agents/{agent_id}`. Apenas os campos fornecidos serão atualizados.

**Exemplo de Atualização:**
```json
PUT /api/agents/123
{
  "name": "Novo Nome",
  "is_favorite": true,
  "workflow_config": {
    "agents": ["agent1", "agent2", "agent3", "agent4"]
  }
}
```

---

## Listagem de Agentes

A listagem de agentes retorna todos os tipos, incluindo os novos campos:

```json
GET /api/agents?limit=20&offset=0

Response:
[
  {
    "id": 1,
    "name": "Meu Agente LLM",
    "agent_type": "llm",
    "model": "gemini/gemini-2.0-flash-exp",
    "instruction": "...",
    "tools": ["..."],
    "use_file_search": false,
    "workflow_config": null,
    "custom_config": null,
    "is_favorite": true,
    "created_at": "2025-11-21T...",
    "updated_at": "2025-11-21T..."
  },
  {
    "id": 2,
    "name": "Pipeline Sequencial",
    "agent_type": "sequential",
    "model": null,
    "instruction": null,
    "tools": null,
    "use_file_search": false,
    "workflow_config": {
      "agents": ["agent1", "agent2", "agent3"]
    },
    "custom_config": null,
    "is_favorite": false,
    "created_at": "2025-11-21T...",
    "updated_at": "2025-11-21T..."
  }
]
```

---

## Notas Importantes

1. **Campos Obrigatórios por Tipo:**
   - LLM: `instruction`, `model`
   - Sequential: `workflow_config.agents` (mínimo 2)
   - Loop: `workflow_config.agent`
   - Parallel: `workflow_config.agents` (mínimo 2)
   - Custom: `custom_config.runtime`, `custom_config.entry_point`, `custom_config.code`

2. **RAG (File Search):**
   - Apenas disponível para agentes LLM
   - Requer modelos Gemini 2.5 Flash
   - Não aplicável a workflow ou custom agents

3. **Validação:**
   - A API valida automaticamente os campos obrigatórios
   - Retorna erro 400 se houver problemas na configuração

4. **Compatibilidade:**
   - Agentes existentes são automaticamente marcados como tipo "llm"
   - Não há necessidade de migração de dados

---

## Swagger/OpenAPI

Acesse a documentação interativa em `/docs` para testar todos os endpoints com exemplos completos de cada tipo de agente.

