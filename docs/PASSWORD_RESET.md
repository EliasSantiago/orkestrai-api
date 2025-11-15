# Password Reset Configuration

## Variáveis de Ambiente Necessárias

Adicione as seguintes variáveis ao seu arquivo `.env`:

```env
# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app
SMTP_FROM_EMAIL=seu-email@gmail.com
SMTP_FROM_NAME=Agents ADK API
SMTP_USE_TLS=true

# Password Reset Settings
PASSWORD_RESET_TOKEN_EXPIRE_HOURS=24
PASSWORD_RESET_BASE_URL=http://localhost:8001
```

## Configuração do Gmail

Se você estiver usando Gmail:

1. **Ative a verificação em duas etapas** na sua conta Google
2. **Gere uma senha de app**:
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "App" e "Email"
   - Selecione "Outro (nome personalizado)" e digite "Agents ADK API"
   - Clique em "Gerar"
   - Use a senha gerada (16 caracteres) como `SMTP_PASSWORD`

## Outros Provedores SMTP

### Outlook/Hotmail
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

### SendGrid
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=sua-api-key-do-sendgrid
```

### Mailgun
```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=seu-usuario-mailgun
SMTP_PASSWORD=sua-senha-mailgun
```

## Endpoints da API

### 1. Solicitar Recuperação de Senha
```bash
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "usuario@example.com"
}
```

**Resposta:**
```json
{
  "message": "If the email exists, a password reset link has been sent.",
  "status": "success"
}
```

### 2. Redefinir Senha
```bash
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "token-do-email",
  "email": "usuario@example.com",
  "new_password": "novaSenha123",
  "password_confirm": "novaSenha123"
}
```

**Resposta:**
```json
{
  "message": "Password has been reset successfully",
  "status": "success"
}
```

## Fluxo de Recuperação

1. Usuário solicita recuperação via `POST /api/auth/forgot-password`
2. Sistema gera token único e temporário (válido por 24h por padrão)
3. Email é enviado com link contendo token e email como query parameters
4. Usuário clica no link e é redirecionado para frontend
5. Frontend extrai token e email da URL
6. Frontend envia requisição para `POST /api/auth/reset-password` com token, email e nova senha
7. Sistema valida token, atualiza senha e marca token como usado

## Segurança

- ✅ Tokens expiram automaticamente após o tempo configurado
- ✅ Tokens são marcados como usados após reset bem-sucedido
- ✅ Tokens não podem ser reutilizados
- ✅ Email enumeration prevention: sempre retorna sucesso mesmo se email não existir
- ✅ Validação de correspondência entre token e email
- ✅ Senhas são hasheadas com bcrypt antes de salvar

## Notas

- Se o email não estiver configurado, o sistema apenas logará o link no console (útil para desenvolvimento)
- O link no email aponta para `PASSWORD_RESET_BASE_URL/reset-password?token=...&email=...`
- Você precisa criar um frontend que capture esses parâmetros e permita ao usuário digitar a nova senha

