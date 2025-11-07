# Troubleshooting - Erro 429 (Resource Exhausted)

## Erro: 429 RESOURCE_EXHAUSTED

Este erro ocorre quando você excede o limite de requisições da API do Google Gemini.

### Mensagem de Erro

```
HTTP/1.1 429 Too Many Requests
ERROR: 429 RESOURCE_EXHAUSTED
Resource exhausted. Please try again later.
```

### Causas

1. **Limite de taxa (Rate Limit)**: Você fez muitas requisições em um curto período
2. **Limite de quota**: Você atingiu o limite diário/mensal da sua conta
3. **Múltiplas requisições simultâneas**: Muitas requisições ao mesmo tempo

### Soluções

#### 1. Aguardar e Tentar Novamente

O erro 429 é temporário. Aguarde alguns minutos e tente novamente:

```bash
# Aguarde 1-2 minutos e tente novamente
```

#### 2. Verificar Quotas da API

1. Acesse: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
2. Verifique seus limites de quota
3. Se necessário, solicite aumento de quota

#### 3. Reduzir Requisições

- Evite fazer muitas requisições em sequência
- Adicione delays entre requisições se estiver testando
- Use um único agente por vez durante testes

#### 4. Verificar API Key

Certifique-se de que sua API key está configurada corretamente:

```bash
# Verificar .env
cat .env | grep GOOGLE_API_KEY
```

#### 5. Usar Modelo Diferente

Se o modelo `gemini-2.0-flash-exp` estiver com limite, tente outro:

- `gemini-1.5-pro`
- `gemini-1.5-flash`

Edite o agente via API para usar outro modelo.

### Prevenção

1. **Implementar retry com backoff**: O ADK já tem retry logic, mas pode demorar
2. **Monitorar uso**: Acompanhe suas requisições no Google Cloud Console
3. **Usar cache**: Para respostas idênticas, considere implementar cache
4. **Limitar requisições simultâneas**: Evite muitas requisições ao mesmo tempo

### Limites Comuns

- **Free Tier**: Geralmente 15-60 requisições por minuto
- **Paid Tier**: Limites mais altos, dependendo do plano

### Verificação Rápida

```bash
# Verificar se o erro persiste após alguns minutos
# O erro 429 é temporário e geralmente se resolve sozinho
```

### Quando Contatar Suporte

Se o erro persistir por mais de 1 hora e você não tiver feito muitas requisições:

1. Verifique o Google Cloud Console para mensagens
2. Verifique se sua conta está ativa
3. Entre em contato com o suporte do Google Cloud

### Nota Importante

O erro 429 **não é um bug do código**, mas sim um limite de taxa da API. O sistema está funcionando corretamente - você apenas atingiu o limite de requisições permitidas.

