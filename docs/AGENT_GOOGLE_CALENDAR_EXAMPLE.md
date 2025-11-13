# Exemplo de Agente: Assistente de Google Calendar

## 🎯 Agente Completo com Todas as Ferramentas

Este exemplo mostra como criar um agente que usa **todas as ferramentas disponíveis** do Google Calendar MCP.

## 📋 Ferramentas Disponíveis

O Google Calendar MCP oferece as seguintes ferramentas:

- `google_calendar_create_event` - Criar novo evento
- `google_calendar_list_events` - Listar eventos
- `google_calendar_get_event` - Obter evento específico
- `google_calendar_update_event` - Atualizar evento
- `google_calendar_delete_event` - Deletar evento
- `google_calendar_list_calendars` - Listar calendários

## 🤖 Exemplo de Agente Completo

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
  ]
}
```

## 🚀 Como Criar o Agente

### Via API

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
    ]
  }'
```

### Via Swagger UI

1. Acesse: `http://localhost:8001/docs`
2. Vá em **POST /api/agents**
3. Clique em **"Try it out"**
4. Cole o JSON do agente acima
5. Clique em **"Execute"**

## 📝 Exemplos de Uso

### Criar Evento

```
Usuário: "Crie um evento para reunião de equipe amanhã às 14h"

Agente: "Perfeito! Vou criar um evento de reunião de equipe. Preciso de algumas informações:
- Qual o título completo do evento?
- Quanto tempo dura a reunião?
- Onde será a reunião? (opcional)
- Algum participante para adicionar? (opcional)"

[Após coletar informações, cria o evento]
```

### Listar Eventos

```
Usuário: "Quais eventos tenho esta semana?"

Agente: "Vou listar seus eventos desta semana..."

[Usa google_calendar_list_events com time_min e time_max]
[Apresenta eventos de forma organizada]
```

### Atualizar Evento

```
Usuário: "Mude o horário da reunião de amanhã para 15h"

Agente: "Vou buscar a reunião de amanhã e atualizar o horário..."

[Busca eventos, encontra o evento, atualiza]
```

### Deletar Evento

```
Usuário: "Delete o evento de consulta médica"

Agente: "Encontrei o evento 'Consulta Médica' no dia X. Tem certeza que deseja deletar?"

[Confirma e deleta]
```

## 🔍 Verificar Ferramentas Disponíveis

Antes de criar o agente, você pode verificar quais ferramentas estão disponíveis:

```bash
curl -X GET 'http://localhost:8001/api/mcp/tools/google_calendar' \
  -H 'Authorization: Bearer SEU_TOKEN_JWT'
```

Isso retorna todas as ferramentas que você pode usar no array `tools` do agente.

## ✅ Checklist

- [ ] Google Calendar conectado (você já fez isso! ✅)
- [ ] Verificou ferramentas disponíveis via `/api/mcp/tools/google_calendar`
- [ ] Criou o agente com todas as ferramentas
- [ ] Testou criando um evento
- [ ] Testou listando eventos
- [ ] Testou atualizando um evento

## 🎯 Dicas

1. **Sempre pergunte detalhes**: O agente deve perguntar título, data/hora, etc. antes de criar eventos
2. **Confirme ações destrutivas**: Sempre confirme antes de deletar eventos
3. **Use português**: O agente deve se comunicar em português brasileiro
4. **Formato de datas**: Use ISO 8601 para datas/horas (ex: `2024-01-15T14:00:00-03:00`)

## 📚 Próximos Passos

Após criar o agente:

1. **Teste criando um evento**: "Crie um evento de teste para amanhã às 10h"
2. **Teste listando eventos**: "Quais eventos tenho hoje?"
3. **Teste atualizando**: "Mude o horário do evento de teste para 11h"
4. **Teste deletando**: "Delete o evento de teste"

Pronto para usar! 🎉

