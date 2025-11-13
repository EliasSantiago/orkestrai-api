# 🔧 Como Resolver Erro 403: Access Blocked

## ❌ Erro Comum

Ao tentar autorizar o Google Calendar, você pode receber:

```
Access blocked: MCP Calendar Integration has not completed the Google verification process
Error 403: access denied
```

## 🎯 Causa

A aplicação OAuth está configurada como **"Testing"** (em teste) no Google Cloud Console, e o usuário que está tentando acessar **não está na lista de testadores**.

## ✅ Solução: Adicionar Usuário de Teste

### Passo a Passo

1. **Acesse Google Cloud Console**
   - https://console.cloud.google.com/
   - Selecione seu projeto

2. **Vá para OAuth Consent Screen**
   - Menu lateral: **"APIs & Services"** → **"OAuth consent screen"**

3. **Encontre a Seção "Test users"**
   - Role a página até encontrar **"Test users"** (ou "Usuários de teste")
   - Esta seção aparece após configurar as informações básicas do app

4. **Adicionar Usuário**
   - Clique em **"+ ADD USERS"** (ou "+ ADICIONAR USUÁRIOS")
   - Digite o email do usuário que precisa acessar
   - Exemplo: `contatovoilabeatriz@gmail.com`
   - Clique em **"ADD"** (ou "ADICIONAR")

5. **Pronto!**
   - O usuário agora pode acessar a aplicação
   - Pode adicionar até 100 usuários de teste

### Visualização no Console

```
OAuth consent screen
├── App information
├── App domain
├── Authorized domains
├── Developer contact information
└── Test users  ← AQUI!
    └── + ADD USERS
```

## 🔄 Após Adicionar Usuário

1. O usuário deve **fazer logout** do Google (se estiver logado)
2. Tentar novamente o fluxo OAuth
3. Agora deve funcionar!

## 📝 Alternativa: Publicar Aplicação

Se quiser que **qualquer usuário** possa acessar (sem adicionar manualmente):

1. Vá em **"OAuth consent screen"**
2. Clique em **"PUBLISH APP"** (ou "PUBLICAR APLICATIVO")
3. Confirme a publicação

**⚠️ ATENÇÃO**: 
- Publicar pode exigir verificação do Google
- Para desenvolvimento/testes, é mais fácil usar "Test users"
- Aplicações publicadas podem levar alguns dias para serem aprovadas

## 🎯 Resumo

| Situação | Solução |
|----------|---------|
| **Desenvolvimento/Testes** | Adicionar usuários em "Test users" |
| **Produção (poucos usuários)** | Adicionar usuários em "Test users" |
| **Produção (muitos usuários)** | Publicar aplicação (pode exigir verificação) |

## ✅ Checklist

- [ ] Acessei Google Cloud Console
- [ ] Naveguei para "OAuth consent screen"
- [ ] Encontrei seção "Test users"
- [ ] Adicionei email do usuário
- [ ] Usuário fez logout do Google
- [ ] Testei novamente o fluxo OAuth
- [ ] Funcionou! ✅

## 📚 Referências

- [Google OAuth Testing](https://developers.google.com/identity/protocols/oauth2/policy#testing)
- [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)

