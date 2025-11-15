# Tipos de Grant OAuth para API On-Premise

Este documento explica quando você precisa de username/password e quando não precisa.

## 🔐 Tipos de Grant OAuth

A aplicação suporta dois tipos de grant OAuth:

### 1. Password Grant (Padrão)

**Quando usar:** Quando a API exige username e password no body da requisição de token.

**Exemplo de curl:**
```bash
curl -X POST https://apidesenv.go.gov.br/token \
  -d "grant_type=password&username=Username&password=Password" \
  -H "Authorization: Basic {consumer_key:secret_base64}"
```

**Configuração necessária:**
```env
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token
ONPREMISE_CONSUMER_KEY=X1mgu5MTHdp6VxZEemXCLZ2FGloa
ONPREMISE_CONSUMER_SECRET=d1z8Pg2ZmHrZz9aFsuUlAFKRn7Aa
ONPREMISE_USERNAME=seu_usuario          # ← NECESSÁRIO
ONPREMISE_PASSWORD=sua_senha            # ← NECESSÁRIO
ONPREMISE_OAUTH_GRANT_TYPE=password     # (padrão, opcional)
```

### 2. Client Credentials Grant

**Quando usar:** Quando a API NÃO exige username/password, apenas consumer key/secret.

**Exemplo de curl:**
```bash
curl -X POST https://apidesenv.go.gov.br/token \
  -d "grant_type=client_credentials" \
  -H "Authorization: Basic {consumer_key:secret_base64}"
```

**Configuração necessária:**
```env
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token
ONPREMISE_CONSUMER_KEY=X1mgu5MTHdp6VxZEemXCLZ2FGloa
ONPREMISE_CONSUMER_SECRET=d1z8Pg2ZmHrZz9aFsuUlAFKRn7Aa
ONPREMISE_OAUTH_GRANT_TYPE=client_credentials  # ← Define o tipo
# ONPREMISE_USERNAME e ONPREMISE_PASSWORD NÃO são necessários
```

## ❓ Por que você precisa de username/password?

Baseado no seu exemplo de curl:

```bash
curl -k -X POST https://apidesenv.go.gov.br/token \
  -d "grant_type=password&username=Username&password=Password" \
  -H "Authorization: Basic WDFtZ3U1TVRIZHA2VnhaRWVtWENMWjJGR2xvYTpkMXo4UGcyWm1Iclp6OWFGc3VVbEFGS1JuN0Fh"
```

Sua API usa **Password Grant** porque:
- ✅ O body contém `grant_type=password`
- ✅ O body contém `username=Username`
- ✅ O body contém `password=Password`

**Portanto, você PRECISA** configurar username e password no `.env`.

## 🔍 Como descobrir qual grant type usar?

### Verifique a documentação da API

1. **Se a documentação mostra username/password no body:**
   - Use `grant_type=password`
   - Configure `ONPREMISE_USERNAME` e `ONPREMISE_PASSWORD`

2. **Se a documentação mostra apenas grant_type=client_credentials:**
   - Use `grant_type=client_credentials`
   - NÃO precisa de username/password

### Teste manualmente

```bash
# Teste 1: Password Grant
curl -X POST https://apidesenv.go.gov.br/token \
  -d "grant_type=password&username=test&password=test" \
  -H "Authorization: Basic {base64_key:secret}"

# Teste 2: Client Credentials
curl -X POST https://apidesenv.go.gov.br/token \
  -d "grant_type=client_credentials" \
  -H "Authorization: Basic {base64_key:secret}"
```

O que funcionar é o tipo correto.

## 📝 Resumo

| Grant Type | Consumer Key/Secret | Username/Password | Quando Usar |
|------------|---------------------|-------------------|-------------|
| `password` | ✅ Obrigatório | ✅ Obrigatório | API exige credenciais de usuário |
| `client_credentials` | ✅ Obrigatório | ❌ Não precisa | API usa apenas consumer key/secret |

## ⚙️ Configuração Recomendada

Para sua API (baseado no seu curl):

```env
# OAuth Configuration
ONPREMISE_TOKEN_URL=https://apidesenv.go.gov.br/token
ONPREMISE_CONSUMER_KEY=X1mgu5MTHdp6VxZEemXCLZ2FGloa
ONPREMISE_CONSUMER_SECRET=d1z8Pg2ZmHrZz9aFsuUlAFKRn7Aa
ONPREMISE_OAUTH_GRANT_TYPE=password
ONPREMISE_USERNAME=seu_usuario_real    # Substitua pelo seu username real
ONPREMISE_PASSWORD=sua_senha_real      # Substitua pela sua senha real
```

**Nota:** No seu exemplo de curl, você usou `username=Username` e `password=Password` como placeholders. Substitua pelos valores reais no `.env`.

