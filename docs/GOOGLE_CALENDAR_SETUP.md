# Configuração do Google Calendar MCP

## 🎯 Visão Geral

O Google Calendar MCP permite que seus agentes interajam com a agenda dos usuários, criando, listando, atualizando e deletando eventos. Cada usuário conecta sua própria conta do Google.

## 📋 Pré-requisitos

1. **Criar Projeto no Google Cloud**
   - Acesse: https://console.cloud.google.com/
   - Crie um novo projeto ou selecione um existente
   - Habilite a **Google Calendar API**

2. **Configurar OAuth 2.0**
   - Vá em **APIs & Services** → **Credentials**
   - Clique em **Create Credentials** → **OAuth client ID**
   - Escolha **Web application**
   - Configure **Authorized redirect URIs**:
     - Para desenvolvimento: `http://localhost:8001/api/mcp/google_calendar/oauth/callback`
     - Para produção: `https://seu-dominio.com/api/mcp/google_calendar/oauth/callback`
   - Anote o **Client ID** e **Client Secret**

3. **Configurar Scopes**
   - Os scopes necessários são:
     - `https://www.googleapis.com/auth/calendar` (acesso completo ao calendário)
     - `https://www.googleapis.com/auth/calendar.events` (apenas eventos)

## 🔧 Como Conectar

### Opção 1: Via OAuth Flow (Recomendado - Futuro)

Uma implementação completa de OAuth será adicionada em breve. Por enquanto, use a Opção 2.

### Opção 2: Token Manual (Desenvolvimento)

Para desenvolvimento/testes, você pode obter um token manualmente:

1. **Obter Token de Acesso**
   - Use o [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
   - Selecione **Calendar API v3**
   - Autorize e obtenha o **Access Token** e **Refresh Token**

2. **Conectar via API**
   ```bash
   curl -X POST 'http://localhost:8001/api/mcp/connect' \
     -H 'Authorization: Bearer SEU_TOKEN_JWT' \
     -H 'Content-Type: application/json' \
     -d '{
       "provider": "google_calendar",
       "credentials": {
         "access_token": "ya29.a0AfH6SMB...",
         "refresh_token": "1//0g...",
         "client_id": "seu_client_id.apps.googleusercontent.com",
         "client_secret": "seu_client_secret"
       }
     }'
   ```

**Nota**: O `refresh_token` e `client_id`/`client_secret` são opcionais, mas recomendados para permitir refresh automático de tokens.

## 🔍 Verificar Conexão

```bash
curl -X GET 'http://localhost:8001/api/mcp/status/google_calendar' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'
```

## 📝 Listar Ferramentas Disponíveis

```bash
curl -X GET 'http://localhost:8001/api/mcp/tools/google_calendar' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'
```

**Ferramentas disponíveis**:
- `google_calendar_create_event` - Criar novo evento
- `google_calendar_list_events` - Listar eventos
- `google_calendar_get_event` - Obter evento específico
- `google_calendar_update_event` - Atualizar evento
- `google_calendar_delete_event` - Deletar evento
- `google_calendar_list_calendars` - Listar calendários

## 🎯 Exemplo de Agente

```json
{
  "name": "Assistente de Agenda",
  "description": "Agente que gerencia eventos no Google Calendar",
  "instruction": "Você pode criar, listar, atualizar e deletar eventos no Google Calendar. Sempre pergunte detalhes como título, data/hora, localização e participantes antes de criar um evento.",
  "model": "gpt-4o-mini",
  "tools": [
    "google_calendar_create_event",
    "google_calendar_list_events",
    "google_calendar_get_event",
    "google_calendar_update_event",
    "google_calendar_delete_event",
    "google_calendar_list_calendars"
  ]
}
```

## 📚 Exemplos de Uso

### Criar Evento

O agente pode criar eventos naturalmente:
- "Crie um evento para reunião amanhã às 14h"
- "Agende uma consulta médica para 25/12 às 10h"
- "Crie um evento de aniversário no dia 15/01 às 19h"

### Listar Eventos

- "Quais eventos tenho esta semana?"
- "Mostre meus compromissos de hoje"
- "Liste todos os eventos de dezembro"

### Atualizar/Deletar

- "Mude o horário da reunião de amanhã para 15h"
- "Delete o evento de consulta médica"
- "Atualize a localização do evento para 'Sala 203'"

## ⚠️ Troubleshooting

### Erro: "Authentication failed"
- Verifique se o token de acesso está válido
- Tokens expiram após 1 hora; use refresh_token para renovar automaticamente
- Certifique-se de que os scopes corretos foram solicitados

### Erro: "Calendar not found"
- Use `"primary"` como `calendar_id` para o calendário principal
- Use `list_calendars` para ver todos os calendários disponíveis

### Token Expirou
- Se você forneceu `refresh_token`, `client_id` e `client_secret`, o sistema tentará renovar automaticamente
- Caso contrário, você precisará obter um novo token manualmente

## 🔐 Segurança

- Tokens são armazenados criptografados no banco de dados
- Cada usuário só acessa sua própria agenda
- Tokens nunca são expostos em logs ou respostas da API

## 📖 Referências

- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)

