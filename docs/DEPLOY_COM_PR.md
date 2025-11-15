# 🔀 Deploy Automático com Pull Requests

Configuração para fazer deploy automático quando um PR é aprovado e mergeado na branch main.

## 🎯 Como Funciona

O deploy automático é disparado em 3 situações:

### 1. **Push Direto na Main** ✅
```bash
git checkout main
git add .
git commit -m "Minhas mudanças"
git push origin main
# Deploy automático!
```

### 2. **Merge de Pull Request** ✅ (NOVO)
```
1. Criar branch e fazer mudanças
2. Abrir Pull Request para main
3. Aprovar e fazer MERGE do PR
4. Deploy automático quando PR for merged!
```

### 3. **Trigger Manual** ✅
```
GitHub → Actions → Deploy to Google Cloud E2 → Run workflow
```

## 📋 Fluxo com Pull Request

### Passo a Passo:

```bash
# 1. Criar nova branch
git checkout -b feature/nova-funcionalidade

# 2. Fazer suas mudanças
git add .
git commit -m "Adicionar nova funcionalidade"
git push origin feature/nova-funcionalidade

# 3. Abrir PR no GitHub
# Vá em: Pull Requests → New Pull Request
# Base: main ← Compare: feature/nova-funcionalidade

# 4. Revisar código, testar, aprovar

# 5. Merge do PR
# Clique em "Merge pull request"
# Confirme o merge

# 6. Deploy automático é disparado! 🚀
```

## 🔄 Fluxo Visual

```
Branch Feature
    │
    ├─ Commit 1
    ├─ Commit 2
    └─ Commit 3
         │
         ├─ Push para GitHub
         │
         └─ Abrir Pull Request
              │
              ├─ Review do código
              ├─ Testes automáticos (CI)
              ├─ Aprovação
              │
              └─ Merge para Main
                   │
                   └─ 🚀 DEPLOY AUTOMÁTICO!
                        │
                        ├─ Build Docker
                        ├─ Transfer para E2
                        ├─ Deploy
                        └─ ✅ Online!
```

## ⚙️ Configuração do Workflow

O workflow detecta automaticamente se o deploy foi disparado por:

```yaml
# .github/workflows/deploy.yml

on:
  push:
    branches: [main, master]    # Push direto
  
  pull_request:
    types: [closed]              # PR fechado
    branches: [main, master]
  
  workflow_dispatch:             # Manual

jobs:
  build-and-deploy:
    # Só executa se PR foi MERGED (não apenas fechado)
    if: |
      github.event_name == 'push' || 
      github.event_name == 'workflow_dispatch' || 
      (github.event_name == 'pull_request' && 
       github.event.pull_request.merged == true)
```

## 📊 Informações Exibidas no Deploy

Durante o deploy, você verá:

```
🚀 Deploy triggered by: pull_request
📋 PR #42: Adicionar nova funcionalidade
✅ PR merged by: EliasSantiago
🌿 Branch: main
👤 Actor: EliasSantiago
```

## 🔒 Proteção de Branch (Recomendado)

Para garantir qualidade antes do deploy:

### Configurar no GitHub:

1. **Settings → Branches → Add rule**
2. **Branch name pattern:** `main`
3. **Ativar:**
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1)
   - ✅ Require status checks to pass before merging
   - ✅ Require conversation resolution before merging

Isso garante que:
- Ninguém faça push direto na main
- Todo código passe por review
- Testes passem antes do merge
- Deploy só acontece após aprovação

## 🎨 Estratégias de Branching

### Git Flow Simplificado

```
main (produção)
  ├─ feature/nova-api         # Nova funcionalidade
  ├─ fix/corrigir-bug         # Correção de bug
  ├─ hotfix/critical-fix      # Fix crítico
  └─ chore/atualizar-deps     # Manutenção
```

### Nomenclatura de Branches

```bash
# Features
feature/nome-da-funcionalidade

# Bugs
fix/descricao-do-bug

# Hotfixes
hotfix/descricao-urgente

# Chores (manutenção)
chore/atualizar-dependencias
```

## 🧪 CI/CD Completo

```
┌─────────────────────────────────────────────┐
│ 1. Developer cria branch                    │
└───────────────┬─────────────────────────────┘
                │
┌───────────────▼─────────────────────────────┐
│ 2. Push da branch                           │
└───────────────┬─────────────────────────────┘
                │
┌───────────────▼─────────────────────────────┐
│ 3. Abre Pull Request                        │
│    - CI: Testes automáticos                 │
│    - CI: Lint                                │
│    - CI: Build Docker                        │
└───────────────┬─────────────────────────────┘
                │
┌───────────────▼─────────────────────────────┐
│ 4. Code Review                              │
│    - Comentários                             │
│    - Sugestões                               │
│    - Aprovação                               │
└───────────────┬─────────────────────────────┘
                │
┌───────────────▼─────────────────────────────┐
│ 5. Merge para Main                          │
└───────────────┬─────────────────────────────┘
                │
┌───────────────▼─────────────────────────────┐
│ 6. Deploy Automático                        │
│    - Build produção                          │
│    - Deploy em E2                            │
│    - Health check                            │
└───────────────┬─────────────────────────────┘
                │
┌───────────────▼─────────────────────────────┐
│ 7. ✅ Em Produção!                          │
└─────────────────────────────────────────────┘
```

## 📝 Exemplo Prático

### Cenário: Adicionar novo endpoint

```bash
# 1. Criar branch
git checkout -b feature/adicionar-endpoint-status
git push -u origin feature/adicionar-endpoint-status

# 2. Desenvolver
# ... fazer mudanças no código ...
git add src/api/status_routes.py
git commit -m "Adicionar endpoint de status"
git push

# 3. Abrir PR no GitHub
# Title: "Adicionar endpoint de status"
# Description: "Endpoint retorna status dos serviços"

# 4. Aguardar CI passar
# ✅ CI - Testes: Passed
# ✅ CI - Lint: Passed
# ✅ CI - Build Docker: Passed

# 5. Review e aprovação
# Teammate aprova o PR

# 6. Merge
# Clica em "Squash and merge" ou "Merge pull request"

# 7. Deploy automático inicia! 🚀
# Acompanhe em: Actions → Deploy to Google Cloud E2

# 8. Verificar em produção
curl http://34.42.168.19:8001/status
```

## 🔍 Monitorar Deploys

```bash
# Ver histórico de deploys
GitHub → Actions → Deploy to Google Cloud E2

# Ver logs de um deploy específico
Click no workflow → Ver steps

# Verificar na máquina E2
ssh ignitor_online@34.42.168.19
cd ~/orkestrai-api
./scripts/check_server_status.sh
docker logs --tail 50 orkestrai-api
```

## 🚨 Troubleshooting

### PR merged mas deploy não iniciou

**Verificar:**
1. Workflow está ativo? (Actions → Workflows)
2. PR foi merged para `main` ou `master`?
3. Ver logs em Actions

### Deploy falhou após PR

```bash
# 1. Ver logs do workflow no GitHub Actions
# 2. Conectar no servidor e verificar
ssh ignitor_online@34.42.168.19
docker logs orkestrai-api

# 3. Se necessário, fazer rollback
./scripts/rollback.sh
```

### Cancelar deploy em andamento

```
GitHub → Actions → Deploy em execução → Cancel workflow
```

## 💡 Boas Práticas

1. **Sempre abrir PR** (não push direto em main)
2. **Testar localmente** antes de abrir PR
3. **Descrição clara** do que foi mudado
4. **Review de código** por outro developer
5. **Aguardar CI passar** antes de merge
6. **Acompanhar deploy** após merge
7. **Testar em produção** após deploy

## 🎯 Resumo

✅ **3 formas de disparar deploy:**
- Push direto na main
- Merge de Pull Request ⭐ (NOVO)
- Trigger manual

✅ **Deploy só acontece quando PR é MERGED**
- PR apenas fechado (sem merge) = Sem deploy
- PR merged = Deploy automático!

✅ **Informações completas** no log do deploy
- Quem fez o merge
- Número e título do PR
- Branch de origem

---

**Fluxo recomendado:** Feature branch → PR → Review → Merge → Deploy automático! 🚀

