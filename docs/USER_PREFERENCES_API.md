# 🎨 User Preferences API

## 📋 Visão Geral

A API de Preferências do Usuário permite que cada usuário armazene e recupere suas preferências pessoais (tema, idioma, layout, etc) no backend PostgreSQL.

---

## 🚀 Endpoints Implementados

### **1. GET /api/user/preferences**

Busca as preferências do usuário atual.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "theme": "dark",
  "language": "pt-BR",
  "layout": "compact",
  "notifications": true,
  "sidebar_expanded": false,
  "message_sound": true,
  "font_size": "medium"
}
```

**Se o usuário não tiver preferências salvas:**
```json
{}
```

---

### **2. PUT /api/user/preferences**

Atualiza as preferências do usuário (merge com preferências existentes).

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "theme": "dark",
  "language": "pt-BR",
  "layout": "compact"
}
```

**Response (200):**
```json
{
  "theme": "dark",
  "language": "pt-BR",
  "layout": "compact",
  "notifications": true,
  "sidebar_expanded": false
}
```

**Observações:**
- ✅ Aceita qualquer campo JSON (flexível para futuras preferências)
- ✅ Faz merge com preferências existentes (não sobrescreve tudo)
- ✅ Atualiza apenas os campos enviados

---

### **3. DELETE /api/user/preferences**

Reseta as preferências para o padrão (objeto vazio).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Preferences reset successfully"
}
```

---

### **4. GET /api/user/profile**

Busca o perfil completo do usuário (incluindo preferências).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao@example.com",
  "is_active": true,
  "preferences": {
    "theme": "dark",
    "language": "pt-BR"
  },
  "created_at": "2025-11-16T10:00:00",
  "updated_at": "2025-11-16T12:30:00"
}
```

---

## 📊 Preferências Comuns

| Campo | Tipo | Valores Sugeridos | Descrição |
|-------|------|-------------------|-----------|
| `theme` | string | "light", "dark", "auto" | Tema da interface |
| `language` | string | "en", "pt-BR", "es", etc | Idioma |
| `layout` | string | "default", "compact", "comfortable" | Layout |
| `notifications` | boolean | true, false | Notificações |
| `sidebar_expanded` | boolean | true, false | Sidebar expandida |
| `message_sound` | boolean | true, false | Som de mensagem |
| `font_size` | string | "small", "medium", "large" | Tamanho da fonte |

**Observação:** Você pode adicionar qualquer campo personalizado! O sistema é flexível.

---

## 🔧 Instalação/Migração

### **1. Aplicar Migration**

```bash
cd /path/to/orkestrai-api

# Opção 1: Script automático
./scripts/apply_user_preferences_migration.sh

# Opção 2: Manual (se tiver DATABASE_URL configurado)
psql $DATABASE_URL -f migrations/add_user_preferences.sql

# Opção 3: Manual (especificando parâmetros)
psql -h localhost -p 5432 -U postgres -d orkestrai -f migrations/add_user_preferences.sql
```

### **2. Reiniciar Backend**

```bash
# Docker
docker-compose restart backend

# Manual
pkill -f uvicorn
uvicorn src.api.main:app --reload
```

---

## 🧪 Testes

### **Testar com cURL**

```bash
# 1. Fazer login
TOKEN=$(curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# 2. Buscar preferências
curl -X GET http://localhost:8001/api/user/preferences \
  -H "Authorization: Bearer $TOKEN"

# 3. Atualizar preferências
curl -X PUT http://localhost:8001/api/user/preferences \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme":"dark","language":"pt-BR","layout":"compact"}'

# 4. Buscar perfil completo
curl -X GET http://localhost:8001/api/user/profile \
  -H "Authorization: Bearer $TOKEN"

# 5. Resetar preferências
curl -X DELETE http://localhost:8001/api/user/preferences \
  -H "Authorization: Bearer $TOKEN"
```

### **Testar com Swagger UI**

1. Abrir: `http://localhost:8001/docs`
2. Fazer login em `/api/auth/login`
3. Clicar em "Authorize" e colar o token
4. Testar os endpoints de `/api/user/*`

---

## 💻 Exemplo de Integração (Frontend)

### **JavaScript/TypeScript**

```typescript
// Buscar preferências
async function getPreferences() {
  const response = await fetch('http://localhost:8001/api/user/preferences', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
}

// Atualizar preferências
async function updatePreferences(prefs: object) {
  const response = await fetch('http://localhost:8001/api/user/preferences', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(prefs)
  });
  return response.json();
}

// Uso
const prefs = await getPreferences();
console.log('Tema atual:', prefs.theme);

await updatePreferences({ theme: 'dark', language: 'pt-BR' });
```

### **React Hook Example**

```typescript
import { useState, useEffect } from 'react';

function useUserPreferences() {
  const [preferences, setPreferences] = useState({});
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadPreferences() {
      const prefs = await getPreferences();
      setPreferences(prefs);
      setLoading(false);
    }
    loadPreferences();
  }, []);
  
  const updatePref = async (key: string, value: any) => {
    const newPrefs = { ...preferences, [key]: value };
    setPreferences(newPrefs);
    await updatePreferences(newPrefs);
  };
  
  return { preferences, updatePref, loading };
}

// Uso no componente
function ThemeToggle() {
  const { preferences, updatePref } = useUserPreferences();
  
  return (
    <button onClick={() => updatePref('theme', 
      preferences.theme === 'dark' ? 'light' : 'dark'
    )}>
      Toggle Theme
    </button>
  );
}
```

---

## 🗄️ Schema do Banco de Dados

### **Coluna Adicionada:**

```sql
ALTER TABLE users 
ADD COLUMN preferences JSON DEFAULT '{}';
```

### **Exemplo de Dados:**

```sql
SELECT id, email, preferences FROM users;

-- Resultado:
-- id | email                 | preferences
-- ---+-----------------------+----------------------------------
-- 1  | joao@example.com      | {"theme":"dark","language":"pt-BR"}
-- 2  | maria@example.com     | {"theme":"light","layout":"compact"}
-- 3  | pedro@example.com     | {}
```

---

## 🔐 Segurança

- ✅ **Autenticação obrigatória:** Todos os endpoints requerem Bearer token
- ✅ **Isolamento por usuário:** Cada usuário só acessa suas próprias preferências
- ✅ **Validação de token:** FastAPI verifica token JWT automaticamente
- ✅ **Tipo JSON flexível:** Aceita qualquer estrutura (mas valida tipo)

---

## 🎯 Benefícios

1. **Multi-dispositivo:** Preferências sincronizam entre PC, celular, tablet
2. **Persistência:** Não perde ao limpar cache do navegador
3. **Backup:** Dados seguros no PostgreSQL
4. **Flexível:** Pode adicionar novos campos sem migração
5. **Performance:** JSON nativo do PostgreSQL (queries rápidas)

---

## 📊 Estatísticas de Uso

### **Consultar preferências mais usadas:**

```sql
-- Contar quantos usuários usam tema escuro
SELECT 
  COUNT(*) as users_with_dark_theme
FROM users
WHERE preferences->>'theme' = 'dark';

-- Idiomas mais usados
SELECT 
  preferences->>'language' as language,
  COUNT(*) as user_count
FROM users
WHERE preferences->>'language' IS NOT NULL
GROUP BY preferences->>'language'
ORDER BY user_count DESC;
```

---

## 🐛 Troubleshooting

### **Erro: "Column 'preferences' does not exist"**

```bash
# Aplicar migration
./scripts/apply_user_preferences_migration.sh
```

### **Erro: "401 Unauthorized"**

```bash
# Token expirado ou inválido, fazer login novamente
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

### **Preferências não salvam**

```bash
# Verificar se banco está acessível
psql $DATABASE_URL -c "SELECT 1;"

# Verificar logs do backend
docker-compose logs -f backend
```

---

## 🎉 Pronto!

A API de Preferências está implementada e pronta para uso! 🚀

**Próximos Passos:**
1. ✅ Aplicar migration no banco
2. ✅ Reiniciar backend
3. ✅ Testar endpoints
4. ✅ Integrar no frontend

