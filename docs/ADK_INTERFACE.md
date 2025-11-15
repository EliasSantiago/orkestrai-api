# Guia da Interface do ADK

Este guia explica como usar a interface oficial do ADK para testar e interagir com os agentes.

## 📋 Pré-requisitos

- ADK instalado (`google-adk` está no requirements.txt)
- API Key do Google Gemini configurada no arquivo `.env`
- Ambiente virtual ativado

## 🚀 Modo Interativo (CLI)

O ADK fornece uma interface de linha de comando interativa para testar agentes.

### Executar

```bash
./run_adk_interactive.sh
```

Ou manualmente:

```bash
source .venv/bin/activate
adk run
```

### Uso

Quando o modo interativo iniciar, você poderá:
1. Selecionar um agente específico (se solicitado)
2. Digitar mensagens diretamente
3. O ADK processará as mensagens usando o agente selecionado

**Agentes disponíveis:**
- `greeting_agent` - Agente de saudação
- `calculator_agent` - Agente de cálculos
- `root_agent` - Agente principal

**Executar agente específico:**
```bash
./run_adk_interactive.sh greeting_agent
```

## 🌐 Interface Web Integrada

O ADK fornece uma interface web integrada que pode ser iniciada diretamente.

### Iniciar Interface Web (Mais Simples)

```bash
./start_adk_web.sh
```

A interface estará disponível em:
- **Web UI**: http://localhost:8000

Abra o navegador e acesse http://localhost:8000 para usar a interface visual.

## 🔌 Servidor API (Para Integração Externa)

O ADK também fornece um servidor API que pode ser usado com a interface web do ADK (ADK Web) ou para integrações externas.

### Iniciar o Servidor API

```bash
./start_adk_api.sh
```

O servidor estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

### Usar com ADK Web Externa (Opcional)

Para usar a interface web completa do ADK (versão externa):

1. **Clone o ADK Web:**
   ```bash
   git clone https://github.com/google/adk-web.git
   cd adk-web
   ```

2. **Instale as dependências:**
   ```bash
   npm install
   ```

3. **Inicie o ADK Web (em outro terminal):**
   ```bash
   npm run serve --backend=http://localhost:8000
   ```

4. **Acesse a interface:**
   - Abra http://localhost:4200 no navegador

## 📝 Agentes Disponíveis

### greeting_agent
- **Modelo**: Google Gemini
- **Função**: Fornece saudações amigáveis e conversas casuais
- **Exemplo**: "Olá, como você está?"

### calculator_agent
- **Modelo**: Google Gemini
- **Função**: Realiza cálculos matemáticos
- **Exemplo**: "Quanto é 25 * 4 + 10?"

### root_agent
- **Modelo**: Google Gemini
- **Função**: Agente principal que pode ajudar com saudações e cálculos

## 🔧 Configuração

**⚠️ IMPORTANTE:** Os agentes agora são gerenciados via banco de dados PostgreSQL!

### Criar Agentes

1. Inicie a API REST: `./start_api.sh`
2. Acesse `http://localhost:8001/docs`
3. Faça login e crie agentes via `POST /api/agents`

Consulte `AGENT_CREATION_GUIDE.md` para exemplos completos de payloads.

### Estrutura Automática

Os agentes são automaticamente sincronizados do banco de dados para o ADK:
- Agentes são armazenados na tabela `agents` do PostgreSQL
- Sistema gera automaticamente arquivos temporários em `.agents_db/`
- ADK carrega agentes automaticamente ao iniciar

## 🐛 Troubleshooting

### Erro: "No root_agent found for 'examples'"

Este erro ocorre quando o ADK não encontra o `root_agent` na estrutura esperada.

**Solução:**
1. Certifique-se de que há agentes no banco de dados (tabela `agents`)
2. Verifique se os agentes estão ativos (`is_active = true`)
3. Use o script `./start_adk_web.sh` que carrega agentes do banco automaticamente
4. Verifique a conexão com o PostgreSQL: `docker-compose up -d`

**Como criar agentes:**
- Use a API REST em `http://localhost:8001/docs`
- Consulte `AGENT_CREATION_GUIDE.md` para exemplos

### Erro: "ModuleNotFoundError: No module named 'google.adk'"
- Certifique-se de que o ambiente virtual está ativado
- Execute: `pip install -r requirements.txt`

### Erro: "GOOGLE_API_KEY not found"
- Verifique se o arquivo `.env` existe e contém `GOOGLE_API_KEY`
- Certifique-se de que o arquivo está na raiz do projeto

### Servidor API não inicia
- Verifique se a porta 8000 está livre
- Tente alterar a porta no script `start_adk_api.sh`

### ADK Web não conecta
- Verifique se o servidor API está rodando
- Confirme que a URL do backend está correta (http://localhost:8000)

## 📚 Recursos Adicionais

- [Documentação do ADK](https://google.github.io/adk-docs/)
- [ADK Web no GitHub](https://github.com/google/adk-web)
- [Exemplos do ADK](https://github.com/google/adk-examples)

