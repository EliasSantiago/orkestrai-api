# Por que configurar ONPREMISE_MODELS?

## ❓ É Obrigatório?

**NÃO!** A configuração de `ONPREMISE_MODELS` é **opcional**.

## 🎯 Quando Configurar?

### Opção 1: Não Configurar (Recomendado para Flexibilidade)

Se você **NÃO** configurar `ONPREMISE_MODELS`:

```env
# ONPREMISE_MODELS não configurado
```

**Comportamento:**
- ✅ Qualquer nome de modelo será aceito
- ✅ A API on-premise validará se o modelo existe
- ✅ Mais flexível - você pode usar qualquer nome de modelo

**Exemplo:**
```json
{
  "name": "Meu Agente",
  "model": "qualquer-nome-de-modelo",  // ← Qualquer nome funciona
  "instruction": "..."
}
```

### Opção 2: Configurar Lista (Recomendado para Validação)

Se você **configurar** `ONPREMISE_MODELS`:

```env
ONPREMISE_MODELS=modelo1,modelo2,modelo3
```

**Comportamento:**
- ✅ Apenas modelos na lista serão aceitos
- ✅ Validação acontece antes de chamar a API
- ✅ Lista aparece no endpoint `/api/models`
- ✅ Mais seguro - previne erros de digitação

**Exemplo:**
```json
{
  "name": "Meu Agente",
  "model": "modelo1",  // ← Deve estar na lista
  "instruction": "..."
}
```

## 📋 Vantagens de Cada Abordagem

### Sem Configurar (Flexível)
- ✅ Não precisa manter lista atualizada
- ✅ Funciona com qualquer modelo que a API suportar
- ✅ Menos configuração

### Com Lista Configurada (Seguro)
- ✅ Validação antecipada (erro antes de chamar API)
- ✅ Lista visível em `/api/models`
- ✅ Previne erros de digitação
- ✅ Documenta quais modelos estão disponíveis

## 🔍 Como Descobrir os Modelos Disponíveis?

### Opção 1: Consultar Documentação da API

Verifique a documentação da sua API on-premise para ver quais modelos estão disponíveis.

### Opção 2: Testar Manualmente

Crie um agente com um nome de modelo e veja se funciona:

```bash
curl -X POST http://localhost:8001/api/agents \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "name": "Teste",
    "model": "nome-do-modelo",
    "instruction": "Teste"
  }'
```

Se funcionar, o modelo existe. Se não, a API retornará erro.

### Opção 3: Consultar API Diretamente

Algumas APIs têm endpoint para listar modelos:

```bash
curl https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/models \
  -H "Authorization: Bearer SEU_TOKEN"
```

## 💡 Recomendação

**Para começar:** Não configure `ONPREMISE_MODELS`. Use qualquer nome de modelo e deixe a API validar.

**Para produção:** Configure a lista após descobrir quais modelos sua API realmente suporta. Isso adiciona validação e documentação.

## 📝 Exemplo de Configuração Mínima

```env
# Configuração mínima (sem lista de modelos)
ONPREMISE_API_BASE_URL=https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token
ONPREMISE_CONSUMER_KEY=X1mgu5MTHdp6VxZEemXCLZ2FGloa
ONPREMISE_CONSUMER_SECRET=d1z8Pg2ZmHrZz9aFsuUlAFKRn7Aa
VERIFY_SSL=false

# ONPREMISE_MODELS não é necessário!
```

## ✅ Resumo

| Configuração | Comportamento |
|--------------|---------------|
| `ONPREMISE_MODELS` não configurado | Aceita qualquer nome de modelo (API valida) |
| `ONPREMISE_MODELS=modelo1,modelo2` | Aceita apenas modelos na lista |

**Conclusão:** Você **NÃO precisa** configurar `ONPREMISE_MODELS`. É opcional e útil apenas se quiser validação antecipada.

