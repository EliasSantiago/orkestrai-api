# 🔑 Guia Rápido - Obter Secrets do GitHub

## TL;DR - Comandos Diretos

### 1. Obter IP da Máquina E2 (GCP_HOST)

```bash
# Via gcloud
gcloud compute instances list

# Ou dentro da máquina
curl ifconfig.me
```

### 2. Obter Username (GCP_USERNAME)

```bash
# Conecte na máquina E2 e execute:
whoami

# Ou é o usuário que você usa para SSH:
# ssh USUARIO@ip  ← esse USUARIO
```

### 3. Criar Chave SSH (GCP_SSH_KEY)

```bash
# No seu computador LOCAL (não no servidor)

# 1. Gerar chave (aperte ENTER 2x para não usar senha)
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/gcp_deploy_key

# 2. Copiar chave PÚBLICA para servidor
ssh-copy-id -i ~/.ssh/gcp_deploy_key.pub SEU_USUARIO@SEU_IP

# 3. Testar
ssh -i ~/.ssh/gcp_deploy_key SEU_USUARIO@SEU_IP "echo OK"

# 4. Ver chave PRIVADA (copiar TUDO para o GitHub)
cat ~/.ssh/gcp_deploy_key
```

## 📋 Exemplo Prático Completo

Substitua com seus valores:

```bash
# Exemplo: Minha máquina E2
IP_MAQUINA=34.123.45.67
MEU_USUARIO=ignitor

# 1. Gerar chave SSH
cd ~/.ssh
ssh-keygen -t ed25519 -C "github-deploy" -f gcp_deploy_key
# PRESSIONE ENTER 2x (sem senha)

# 2. Enviar chave pública para servidor
ssh-copy-id -i gcp_deploy_key.pub $MEU_USUARIO@$IP_MAQUINA

# 3. Testar conexão
ssh -i gcp_deploy_key $MEU_USUARIO@$IP_MAQUINA "echo 'Funcionou!'"

# 4. Copiar chave privada
cat gcp_deploy_key
# Copie TUDO que aparecer (incluindo BEGIN e END)
```

## 🔧 Adicionar no GitHub

1. Vá em: **Settings → Secrets and variables → Actions**
2. Clique: **New repository secret**
3. Adicione:

| Name | Value | Como Obter |
|------|-------|------------|
| `GCP_HOST` | `34.123.45.67` | `gcloud compute instances list` |
| `GCP_USERNAME` | `ignitor` | `whoami` no servidor |
| `GCP_SSH_KEY` | `-----BEGIN...` | `cat ~/.ssh/gcp_deploy_key` |

## ✅ Verificar se Funcionou

```bash
# Deve conectar SEM pedir senha
ssh -i ~/.ssh/gcp_deploy_key SEU_USUARIO@SEU_IP

# Se funcionar, está pronto para usar no GitHub Actions!
```

## 🆘 Erro Comum: Permission Denied

```bash
# No servidor E2, ajuste permissões:
ssh SEU_USUARIO@SEU_IP
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

**Guia detalhado:** `docs/COMO_OBTER_SECRETS.md`

