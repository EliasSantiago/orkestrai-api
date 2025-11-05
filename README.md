# Agents ADK Application

Aplicação Python para criar e gerenciar agentes de IA utilizando o Agent Development Kit (ADK) do Google, com suporte para modelos LLM da OpenAI e Google Gemini.

## 🚀 Características

- **Google ADK**: Framework para desenvolvimento de agentes de IA
- **Multi-LLM**: Suporte para Google Gemini e OpenAI
- **PostgreSQL**: Banco de dados para persistência de dados
- **Docker Compose**: Configuração simplificada do PostgreSQL
- **API REST**: API completa para gerenciamento de usuários e agentes
- **Autenticação**: Sistema de registro e login com JWT
- **Agentes Persistidos**: Cada usuário pode criar e gerenciar seus próprios agentes
- **Agentes de Teste**: Dois agentes básicos incluídos

## 📋 Pré-requisitos

- Python 3.9 ou superior
- Docker e Docker Compose
- API Keys:
  - Google Gemini API Key
  - OpenAI API Key

## 🛠️ Instalação

### 1. Clone o repositório

```bash
cd /home/ignitor/projects/agents-adk-google
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione suas API keys:

```env
GOOGLE_API_KEY=sua_chave_google_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
DATABASE_URL=postgresql://agentuser:agentpass@localhost:5432/agentsdb
DEFAULT_MODEL_GEMINI=gemini-2.0-flash-exp
DEFAULT_MODEL_OPENAI=gpt-4o-mini
```

### 5. Inicie o PostgreSQL com Docker Compose

```bash
docker-compose up -d
```

Verifique se o serviço está rodando:

```bash
docker-compose ps
```

### 6. Inicialize o banco de dados

```bash
./init_database.sh
```

Isso criará as tabelas `users` e `agents` no PostgreSQL.

## 🎯 Uso

### Opções de Execução

#### 1. Interface do ADK (Recomendado para testes)

**Interface Web do ADK (Mais fácil):**
```bash
./start_adk_web.sh
```
Acesse http://localhost:8000 no navegador

**Modo Interativo do ADK (CLI):**
```bash
./run_adk_interactive.sh
```

**Servidor API do ADK (para integração externa):**
```bash
./start_adk_api.sh
```

#### 2. API REST (Gerenciamento de Usuários e Agentes)

**Iniciar API FastAPI:**
```bash
./start_api.sh
```

Acesse:
- **API**: http://localhost:8001
- **Documentação**: http://localhost:8001/docs

**Funcionalidades:**
- Registro e login de usuários
- CRUD completo de agentes
- Cada usuário gerencia seus próprios agentes

Consulte `API_DOCS.md` para documentação completa da API.

#### 3. Aplicação Customizada

**Usando o script run.sh:**
```bash
./run.sh
```

**Ativando manualmente o ambiente virtual:**
```bash
source .venv/bin/activate  # Linux/Mac
python -m src.main
```

**⚠️ Importante:** Sempre ative o ambiente virtual antes de executar a aplicação, ou use os scripts fornecidos que fazem isso automaticamente.

### Agentes Incluídos

#### 1. Greeting Agent
Agente que fornece saudações amigáveis e pode informar a hora atual.

**Ferramentas:**
- `get_current_time` - Obtém a hora atual em qualquer timezone

**⚠️ IMPORTANTE:** Agentes agora são criados via API REST!

**Como criar agentes:**
1. Inicie a API: `./start_api.sh`
2. Acesse `http://localhost:8001/docs`
3. Faça login e crie agentes via `POST /api/agents`

**Consulte `AGENT_CREATION_GUIDE.md` para exemplos completos de payloads.**

### Ferramentas Compartilhadas

As ferramentas em `/tools` podem ser usadas por qualquer agente:

- **calculator_tool**: Calcula expressões matemáticas de forma segura
- **time_tool**: Obtém informações de data e hora em diferentes timezones

## 📁 Estrutura do Projeto

```
agents-adk-google/
├── agents/                    # ⚠️ DEPRECATED - Agentes agora vêm do banco de dados
│   ├── greeting_agent/
│   │   ├── agent.py          # Agente de saudação com root_agent
│   │   └── __init__.py
│   └── calculator_agent/
│       ├── agent.py          # Agente de cálculos com root_agent
│       └── __init__.py
├── tools/                     # Ferramentas compartilhadas
│   ├── __init__.py
│   ├── calculator_tool.py    # Ferramenta de cálculos
│   └── time_tool.py          # Ferramenta de tempo
├── src/                       # Aplicação customizada (opcional)
│   ├── __init__.py
│   ├── config.py             # Configurações da aplicação
│   ├── database.py           # Conexão e setup do PostgreSQL
│   ├── main.py              # Ponto de entrada principal
│   └── agents/              # Agentes para aplicação customizada
│       ├── __init__.py
│       ├── greeting_agent.py
│       └── calculator_agent.py
├── docker-compose.yml        # Configuração do PostgreSQL
├── requirements.txt          # Dependências Python
├── .env.example             # Exemplo de variáveis de ambiente
├── run.sh                   # Script para executar aplicação customizada
├── run_adk_interactive.sh   # Script para modo interativo ADK
├── start_adk_api.sh         # Script para servidor API ADK
├── start_adk_web.sh         # Script para interface web ADK
├── setup.sh                 # Script de instalação
├── README.md                # Este arquivo
└── ADK_INTERFACE.md         # Guia da interface ADK
```

## 🔧 Configuração Avançada

### Modelos Disponíveis

#### Google Gemini
- `gemini-2.0-flash-exp` (padrão)
- `gemini-1.5-pro`
- `gemini-1.5-flash`

#### OpenAI
- `gpt-4o-mini` (padrão)
- `gpt-4o`
- `gpt-3.5-turbo`

Você pode alterar os modelos padrão no arquivo `.env`.

### Banco de Dados

O PostgreSQL está configurado para rodar na porta `5432` com as seguintes credenciais:

- **Usuário**: `agentuser`
- **Senha**: `agentpass`
- **Database**: `agentsdb`

Para alterar, edite o arquivo `docker-compose.yml` e o `.env`.

## 🧪 Testes

Para testar os agentes, execute a aplicação e use os comandos interativos:

```bash
python -m src.main
```

Exemplo de teste:

```
Você: greet: Olá, bom dia!
Greeting Agent: Olá! Bom dia para você também! Como posso ajudar hoje?

Você: calc: Qual é a raiz quadrada de 144?
Calculator Agent: A raiz quadrada de 144 é 12.
```

## 📝 Desenvolvimento

### Criar um Novo Agente

1. Crie um novo arquivo em `src/agents/`
2. Defina a classe do agente seguindo o padrão dos agentes existentes
3. Importe o agente em `src/agents/__init__.py`
4. Adicione o agente em `src/main.py`

Exemplo:

```python
# src/agents/my_agent.py
from google.adk.agents import Agent
from src.config import Config

class MyAgent:
    def __init__(self):
        self.agent = Agent(
            model=Config.DEFAULT_MODEL_GEMINI,
            name='my_agent',
            description="Descrição do agente",
            instruction="Instruções para o agente",
        )
    
    def process(self, message: str) -> str:
        return self.agent.run(message)
```

## 🐛 Solução de Problemas

### Erro de conexão com o banco de dados

Verifique se o PostgreSQL está rodando:

```bash
docker-compose ps
docker-compose logs postgres
```

### Erro de API Key

Certifique-se de que as variáveis de ambiente estão configuradas corretamente no arquivo `.env`.

### Erro de importação do ADK

Verifique se o ADK foi instalado:

```bash
pip show google-adk
```

Se não estiver instalado:

```bash
pip install google-adk
```

## 📄 Licença

Este projeto é um exemplo de uso do Google ADK.

## 🔗 Recursos

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)

