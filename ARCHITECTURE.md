# Arquitetura da Aplicação

Este documento descreve a arquitetura da aplicação seguindo as melhores práticas do Google ADK.

## 📐 Visão Geral

A aplicação está organizada em camadas claras que facilitam a evolução e manutenção:

```
┌─────────────────────────────────────────────────┐
│           Interface Web do ADK                  │
│         (adk web - http://localhost:8000)      │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│              Agentes ADK                        │
│  agents/                                         │
│  ├── greeting_agent/                           │
│  └── calculator_agent/                          │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│          Ferramentas Compartilhadas            │
│  tools/                                          │
│  ├── calculator_tool.py                          │
│  └── time_tool.py                                │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         Infraestrutura                         │
│  - PostgreSQL (Docker)                          │
│  - Configuração (.env)                          │
│  - Aplicação Customizada (src/)                │
└─────────────────────────────────────────────────┘
```

## 🗂️ Estrutura de Diretórios

### `/agents` - Agentes ADK

Cada agente é um diretório independente seguindo a convenção do ADK:

```
agents/
  <agent_name>/
    agent.py      # Deve conter root_agent
    __init__.py
```

**Características:**
- Cada agente é independente e pode ser executado separadamente
- Cada agente deve ter um `root_agent` definido
- Agentes podem importar e usar ferramentas compartilhadas de `/tools`

**Exemplo:**
```python
# agents/greeting_agent/agent.py
from tools import get_current_time

root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='root_agent',
    tools=[get_current_time],
    # ...
)
```

### `/tools` - Ferramentas Compartilhadas

Ferramentas que podem ser usadas por qualquer agente:

```
tools/
  __init__.py           # Exporta todas as ferramentas
  calculator_tool.py    # Ferramenta de cálculos
  time_tool.py          # Ferramenta de tempo
```

**Características:**
- Ferramentas são funções Python puras ou com dependências mínimas
- Cada ferramenta deve ter docstrings claras
- Ferramentas retornam dicionários com estrutura padronizada

**Exemplo:**
```python
# tools/calculator_tool.py
def calculator(expression: str) -> dict:
    """
    Calculates a mathematical expression safely.
    
    Returns:
        dict with 'status', 'result', 'expression'
    """
    # Implementação...
```

### `/src` - Aplicação Customizada (Opcional)

Código para aplicação customizada que não usa a interface ADK:

```
src/
  config.py          # Configurações centralizadas
  database.py        # Conexão com PostgreSQL
  main.py           # Ponto de entrada customizado
  agents/           # Agentes para uso customizado
```

**Uso:**
- Quando você precisa de uma aplicação customizada além do ADK
- Para integração com outros sistemas
- Para lógica de negócio específica

## 🔄 Fluxo de Dados

### Interface Web ADK

```
Usuário → Interface Web → ADK Router → Agente → Tools → Resposta
```

1. Usuário interage na interface web (http://localhost:8000)
2. ADK roteia para o agente selecionado
3. Agente processa a mensagem usando o modelo LLM
4. Se necessário, agente chama ferramentas de `/tools`
5. Resposta é formatada e retornada ao usuário

### Aplicação Customizada

```
Usuário → src/main.py → Agente Customizado → Resposta
```

## 🛠️ Adicionando Novos Agentes

1. **Criar diretório do agente:**
   ```bash
   mkdir -p agents/meu_agente
   ```

2. **Criar agent.py:**
   ```python
   # agents/meu_agente/agent.py
   from tools import get_current_time  # Importar tools necessárias
   
   root_agent = Agent(
       model='gemini-2.0-flash-exp',
       name='root_agent',
       tools=[get_current_time],
       # ...
   )
   ```

3. **O agente aparecerá automaticamente na interface web**

## 🔧 Adicionando Novas Ferramentas

1. **Criar arquivo da ferramenta:**
   ```python
   # tools/minha_ferramenta.py
   def minha_ferramenta(param: str) -> dict:
       """Descrição da ferramenta."""
       return {'status': 'success', 'result': ...}
   ```

2. **Exportar em `tools/__init__.py`:**
   ```python
   from tools.minha_ferramenta import minha_ferramenta
   __all__ = ['get_current_time', 'calculator', 'minha_ferramenta']
   ```

3. **Usar em qualquer agente:**
   ```python
   from tools import minha_ferramenta
   root_agent = Agent(..., tools=[minha_ferramenta])
   ```

## 📊 Princípios de Design

### 1. Separação de Responsabilidades
- **Agentes**: Lógica de conversação e decisão
- **Tools**: Operações específicas e reutilizáveis
- **Config**: Configurações centralizadas

### 2. Reutilização
- Tools compartilhadas evitam duplicação
- Agentes podem usar múltiplas tools

### 3. Escalabilidade
- Estrutura permite adicionar agentes facilmente
- Tools podem ser estendidas sem modificar agentes

### 4. Manutenibilidade
- Cada componente em seu próprio arquivo
- Documentação clara e estrutura previsível

## 🚀 Evolução da Aplicação

### Fase 1: Básico (Atual)
- 2 agentes simples
- 2 tools básicas
- Interface web ADK

### Fase 2: Intermediário
- Adicionar mais agentes especializados
- Criar tools para integrações (API, banco de dados)
- Adicionar persistência de sessões

### Fase 3: Avançado
- Agentes especializados por domínio
- Tools complexas com cache e retry
- Integração com sistemas externos
- Monitoramento e logging

## 📚 Referências

- [Documentação ADK](https://google.github.io/adk-docs/)
- [Estrutura de Projetos ADK](https://google.github.io/adk-docs/get-started/python/)
- [Criando Tools](https://google.github.io/adk-docs/guides/tools/)

