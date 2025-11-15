# Configuração OAuth 2.0 para Google Calendar

## 🎯 Visão Geral

Para permitir que **outros usuários** usem seus agentes para interagir com o Google Calendar, você precisa configurar OAuth 2.0 no Google Cloud. Cada usuário conectará sua própria conta do Google, garantindo que os agentes acessem apenas o calendário daquele usuário específico.

## 📋 Passo a Passo Completo

### 1. Criar Projeto no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Clique em **"Select a project"** → **"New Project"**
3. Dê um nome ao projeto (ex: "Agents Calendar Integration")
4. Clique em **"Create"**

### 2. Habilitar Google Calendar API

1. No menu lateral, vá em **"APIs & Services"** → **"Library"**
2. Busque por **"Google Calendar API"**
3. Clique em **"Google Calendar API"**
4. Clique em **"Enable"**

### 3. Configurar Tela de Consentimento OAuth

1. Vá em **"APIs & Services"** → **"OAuth consent screen"**
2. Escolha **"External"** (para permitir que usuários externos se conectem)
3. Preencha as informações:
   - **App name**: Nome da sua aplicação (ex: "Agents Calendar")
   - **User support email**: Seu email
   - **Developer contact information**: Seu email
4. Clique em **"Save and Continue"**
5. Em **"Scopes"**, clique em **"Add or Remove Scopes"**
   - Adicione: `https://www.googleapis.com/auth/calendar`
   - Ou: `https://www.googleapis.com/auth/calendar.events` (mais restritivo)
6. Clique em **"Update"** → **"Save and Continue"**
7. Em **"Test users"** (se ainda estiver em modo de teste):
   - Adicione emails de usuários que podem testar
   - Ou pule se já estiver em produção
8. Clique em **"Save and Continue"** → **"Back to Dashboard"**

### 4. Criar Credenciais OAuth 2.0

1. Vá em **"APIs & Services"** → **"Credentials"**
2. Clique em **"Create Credentials"** → **"OAuth client ID"**
3. Se solicitado, escolha **"Web application"**
4. Configure:
   - **Name**: "Agents Calendar OAuth Client"
   - **Authorized JavaScript origins**:
     - `http://localhost:8001` (desenvolvimento)
     - `https://seu-dominio.com` (produção)
   - **Authorized redirect URIs**:
     - `http://localhost:8001/api/mcp/google_calendar/oauth/callback` (desenvolvimento)
     - `https://seu-dominio.com/api/mcp/google_calendar/oauth/callback` (produção)
5. Clique em **"Create"**
6. **IMPORTANTE**: Anote:
   - **Client ID** (ex: `123456789-abc.apps.googleusercontent.com`)
   - **Client Secret** (ex: `GOCSPX-abc123...`)

### 5. Adicionar Variáveis de Ambiente

Adicione ao seu `.env`:

```env
# Google Calendar OAuth Configuration
GOOGLE_CALENDAR_CLIENT_ID=seu_client_id.apps.googleusercontent.com
GOOGLE_CALENDAR_CLIENT_SECRET=GOCSPX-seu_client_secret
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:8001/api/mcp/google_calendar/oauth/callback
```

**Para produção**, atualize o `REDIRECT_URI`:
```env
GOOGLE_CALENDAR_REDIRECT_URI=https://seu-dominio.com/api/mcp/google_calendar/oauth/callback
```

### 6. Adicionar Usuários de Teste (IMPORTANTE - Resolve Erro 403)

**⚠️ ERRO COMUM**: Se você receber "Access blocked: app has not completed the Google verification process" (Erro 403), significa que a aplicação está em modo de teste e o usuário não está na lista de testadores.

**Solução Rápida - Adicionar Usuário de Teste**:

1. No Google Cloud Console, vá em **"APIs & Services"** → **"OAuth consent screen"**
2. Role até a seção **"Test users"** (ou "Usuários de teste")
3. Clique em **"+ ADD USERS"** (ou "+ ADICIONAR USUÁRIOS")
4. Adicione o email do usuário que precisa acessar (ex: `contatovoilabeatriz@gmail.com`)
5. Clique em **"ADD"** (ou "ADICIONAR")
6. O usuário agora pode acessar a aplicação

**Nota**: Você pode adicionar até 100 usuários de teste.

### 7. Publicar Aplicação (Opcional - para Produção)

Se quiser que **qualquer usuário** possa se conectar (não apenas test users):

1. Vá em **"OAuth consent screen"**
2. Clique em **"PUBLISH APP"** (ou "PUBLICAR APLICATIVO")
3. Confirme a publicação

**⚠️ ATENÇÃO**: Publicar a aplicação pode exigir verificação do Google se você usar scopes sensíveis. Para desenvolvimento, é mais fácil usar "Test users".

## 🔄 Fluxo de Autorização

### Como Funciona

1. **Usuário inicia conexão**:
   ```bash
   GET /api/mcp/google_calendar/oauth/authorize
   Authorization: Bearer {token_jwt_do_usuario}
   ```

2. **Sistema redireciona para Google**:
   - Usuário vê tela de consentimento do Google
   - Usuário autoriza acesso ao calendário

3. **Google redireciona de volta**:
   - Google envia código de autorização
   - Sistema troca código por access_token e refresh_token
   - Tokens são armazenados criptografados no banco

4. **Pronto!** Usuário pode usar agentes com Google Calendar

## 📝 Endpoints Necessários (a implementar)

Você precisará implementar estes endpoints:

### 1. Iniciar Fluxo OAuth
```
GET /api/mcp/google_calendar/oauth/authorize
Authorization: Bearer {token_jwt}
```

**Resposta**: Redireciona para Google OAuth

### 2. Callback OAuth
```
GET /api/mcp/google_calendar/oauth/callback?code={code}&state={state}
```

**Processo**:
- Recebe código de autorização
- Troca por access_token e refresh_token
- Armazena no banco (criptografado)
- Retorna sucesso

## 🔐 Scopes Necessários

### Opção 1: Acesso Completo (Recomendado)
```
https://www.googleapis.com/auth/calendar
```
- Permite criar, ler, atualizar e deletar eventos
- Acesso a todos os calendários do usuário

### Opção 2: Apenas Eventos (Mais Restritivo)
```
https://www.googleapis.com/auth/calendar.events
```
- Apenas operações com eventos
- Não permite gerenciar calendários

## ⚙️ Configuração no Código

### Adicionar ao `src/config.py`:

```python
# Google Calendar OAuth Configuration
GOOGLE_CALENDAR_CLIENT_ID = os.getenv("GOOGLE_CALENDAR_CLIENT_ID", "")
GOOGLE_CALENDAR_CLIENT_SECRET = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET", "")
GOOGLE_CALENDAR_REDIRECT_URI = os.getenv(
    "GOOGLE_CALENDAR_REDIRECT_URI",
    "http://localhost:8001/api/mcp/google_calendar/oauth/callback"
)
```

## 🚀 Exemplo de Implementação OAuth

Aqui está um exemplo de como implementar os endpoints OAuth:

### `src/api/google_calendar_oauth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import httpx
import base64
from jose import jwt
from datetime import datetime, timedelta
from src.config import Config
from src.database import get_db
from src.models import MCPConnection
from src.auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/mcp/google_calendar/oauth", tags=["google-calendar-oauth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

@router.get("/authorize")
async def authorize_google_calendar(user_id: int = Depends(get_current_user_id)):
    """Inicia fluxo OAuth do Google Calendar."""
    if not Config.GOOGLE_CALENDAR_CLIENT_ID:
        raise HTTPException(500, "Google Calendar OAuth not configured")
    
    # Criar state token para segurança
    state = jwt.encode(
        {"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes=10)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    params = {
        "client_id": Config.GOOGLE_CALENDAR_CLIENT_ID,
        "redirect_uri": Config.GOOGLE_CALENDAR_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar",
        "access_type": "offline",  # Para obter refresh_token
        "prompt": "consent",  # Força mostrar tela de consentimento
        "state": state
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Recebe callback do Google OAuth."""
    # Verificar state
    try:
        payload = jwt.decode(state, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except:
        raise HTTPException(400, "Invalid state token")
    
    # Trocar código por tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": Config.GOOGLE_CALENDAR_CLIENT_ID,
                "client_secret": Config.GOOGLE_CALENDAR_CLIENT_SECRET,
                "redirect_uri": Config.GOOGLE_CALENDAR_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(400, f"Failed to exchange code: {response.text}")
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        
        # Armazenar no banco
        credentials = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "client_id": Config.GOOGLE_CALENDAR_CLIENT_ID,
            "client_secret": Config.GOOGLE_CALENDAR_CLIENT_SECRET
        }
        
        # Verificar se já existe conexão
        existing = db.query(MCPConnection).filter(
            MCPConnection.user_id == user_id,
            MCPConnection.provider == "google_calendar"
        ).first()
        
        if existing:
            existing.set_credentials(credentials)
            existing.is_active = True
        else:
            connection = MCPConnection(
                user_id=user_id,
                provider="google_calendar",
                is_active=True
            )
            connection.set_credentials(credentials)
            db.add(connection)
        
        db.commit()
        
        return {"status": "success", "message": "Google Calendar connected successfully"}
```

## ✅ Checklist de Configuração

- [ ] Projeto criado no Google Cloud
- [ ] Google Calendar API habilitada
- [ ] Tela de consentimento OAuth configurada
- [ ] Scopes adicionados (`calendar` ou `calendar.events`)
- [ ] Credenciais OAuth criadas (Client ID e Secret)
- [ ] Redirect URIs configuradas (desenvolvimento e produção)
- [ ] Variáveis de ambiente adicionadas ao `.env`
- [ ] Endpoints OAuth implementados (ou usar implementação acima)
- [ ] Testado com usuário de teste
- [ ] Aplicação publicada (se necessário para produção)

## 🔍 Verificar Configuração

Após configurar, teste:

1. **Verificar se API está habilitada**:
   - Google Cloud Console → APIs & Services → Enabled APIs
   - Deve aparecer "Calendar API"

2. **Verificar credenciais**:
   - Google Cloud Console → APIs & Services → Credentials
   - Deve aparecer seu OAuth 2.0 Client ID

3. **Testar fluxo OAuth**:
   ```bash
   # Iniciar autorização
   curl -X GET 'http://localhost:8001/api/mcp/google_calendar/oauth/authorize' \
     -H 'Authorization: Bearer SEU_TOKEN_JWT' \
     -L
   ```

## 📚 Referências

- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [OAuth Consent Screen](https://developers.google.com/identity/protocols/oauth2/openid-connect#consentscreen)

## ⚠️ Importante

1. **Client Secret**: Nunca exponha o Client Secret publicamente
2. **Redirect URIs**: Devem corresponder exatamente (incluindo http/https, porta, etc.)
3. **Scopes**: Solicite apenas os scopes necessários
4. **Test Users**: Em modo de teste, apenas usuários adicionados podem se conectar
5. **Tokens**: Access tokens expiram em 1 hora; refresh tokens são longos (ou indefinidos)

