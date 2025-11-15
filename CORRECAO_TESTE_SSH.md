# 🔧 Correção - Teste de SSH

## ❌ Erro que você teve:

```bash
ssh -i ~/.ssh/gcp_deploy_key ignitor_online@34.42.168.19 "echo 'SSH OK!'"
# bash: !': event not found
```

**Causa:** O `!` causa expansão de histórico no bash

## ✅ Soluções (use qualquer uma):

### Opção 1: Sem o ponto de exclamação
```bash
ssh -i ~/.ssh/gcp_deploy_key ignitor_online@34.42.168.19 "echo 'SSH OK'"
```

### Opção 2: Usar aspas duplas
```bash
ssh -i ~/.ssh/gcp_deploy_key ignitor_online@34.42.168.19 "echo SSH_OK"
```

### Opção 3: Comando mais simples
```bash
ssh -i ~/.ssh/gcp_deploy_key ignitor_online@34.42.168.19 "whoami"
```

### Opção 4: Testar apenas conexão
```bash
ssh -i ~/.ssh/gcp_deploy_key ignitor_online@34.42.168.19 "hostname"
```

## 🧪 TESTE AGORA COM SEUS DADOS:

```bash
# Seu usuário: ignitor_online
# Seu IP: 34.42.168.19

ssh -i ~/.ssh/gcp_deploy_key ignitor_online@34.42.168.19 "echo Conexao_OK"
```

Se funcionar sem pedir senha → Tudo certo! ✅

## 📋 Seus Secrets para o GitHub:

```
GCP_HOST = 34.42.168.19
GCP_USERNAME = ignitor_online
GCP_SSH_KEY = [conteúdo de: cat ~/.ssh/gcp_deploy_key]
```
