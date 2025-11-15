# 🔑 Como Obter os Secrets do GitHub

Guia passo a passo para obter as informações necessárias para configurar os secrets do GitHub Actions.

## 📋 Secrets Necessários

Você precisa configurar estes 3 secrets no GitHub:
1. **GCP_HOST** - IP externo da máquina E2
2. **GCP_USERNAME** - Usuário SSH
3. **GCP_SSH_KEY** - Chave privada SSH

---

## 1️⃣ GCP_HOST - Obter IP da Máquina E2

### Opção A: Via Console Web do Google Cloud

1. Acesse: https://console.cloud.google.com/compute/instances
2. Localize sua instância E2
3. Na coluna **"External IP"**, copie o IP externo
4. Exemplo: `34.123.45.67`

### Opção B: Via gcloud CLI

```bash
# Listar todas as instâncias
gcloud compute instances list

# Ver apenas o IP externo de uma instância específica
gcloud compute instances describe NOME_DA_INSTANCIA \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### Opção C: Via SSH (dentro da máquina)

```bash
# Conecte-se à máquina E2 e execute:
curl ifconfig.me
# ou
curl icanhazip.com
```

**✅ Resultado:** Um IP no formato `34.123.45.67`

---

## 2️⃣ GCP_USERNAME - Obter Usuário SSH

O username é o **nome de usuário que você usa para conectar via SSH** na máquina E2.

### Como Identificar seu Username

#### Se você JÁ conecta via SSH:

```bash
# O username é a parte ANTES do @
ssh SEU_USUARIO@IP_DA_MAQUINA

# Exemplo: se você conecta com:
ssh joao@34.123.45.67
# Então seu username é: joao
```

#### Se você NÃO sabe qual username:

**Via Console Web do Google Cloud:**

1. Acesse: https://console.cloud.google.com/compute/instances
2. Clique no nome da sua instância E2
3. Clique em **"SSH"** no topo (abre terminal no navegador)
4. Dentro do terminal, execute:
   ```bash
   whoami
   ```
5. O resultado é seu username (ex: `joao_silva`, `ignitor`, etc)

**Via gcloud CLI:**

```bash
# Ver usuários configurados
gcloud compute config-ssh --dry-run

# Ou conectar e verificar
gcloud compute ssh NOME_DA_INSTANCIA
whoami
```

#### Usernames Comuns no Google Cloud:

- Nome da sua conta Google (antes do @gmail.com)
- Nome configurado no projeto GCP
- Geralmente algo como: `seu_nome`, `seunome123`, etc

**✅ Resultado:** Nome de usuário como `joao`, `ignitor`, `admin`, etc

---

## 3️⃣ GCP_SSH_KEY - Gerar e Configurar Chave SSH

Esta é a parte mais importante! Você precisa **GERAR uma NOVA chave SSH** especificamente para o GitHub Actions.

### 🚨 IMPORTANTE: 
**NÃO use sua chave SSH pessoal!** Crie uma nova chave dedicada para o GitHub Actions.

### Passo a Passo Completo

#### **PASSO 1: Gerar Nova Chave SSH (no seu computador local)**

```bash
# No seu computador (não no servidor E2)
cd ~/.ssh

# Gerar chave ED25519 (mais segura e rápida)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f gcp_deploy_key

# O comando vai perguntar:
# Enter passphrase (empty for no passphrase): 
# PRESSIONE ENTER (deixe vazio - GitHub Actions não pode usar senha)

# Confirme:
# Enter same passphrase again:
# PRESSIONE ENTER novamente
```

**Resultado:** Cria 2 arquivos:
- `~/.ssh/gcp_deploy_key` - Chave PRIVADA (vai para o GitHub Secret)
- `~/.ssh/gcp_deploy_key.pub` - Chave PÚBLICA (vai para o servidor E2)

#### **PASSO 2: Copiar Chave PÚBLICA para o Servidor E2**

Você tem várias opções:

**Opção A: Comando Direto (mais fácil)**

```bash
# Copia automaticamente a chave pública para o servidor
ssh-copy-id -i ~/.ssh/gcp_deploy_key.pub SEU_USUARIO@IP_DA_MAQUINA

# Exemplo:
ssh-copy-id -i ~/.ssh/gcp_deploy_key.pub joao@34.123.45.67

# Digite sua senha quando solicitado
```

**Opção B: Manual (se ssh-copy-id não funcionar)**

```bash
# 1. Ver conteúdo da chave pública
cat ~/.ssh/gcp_deploy_key.pub

# 2. Copie TODO o conteúdo (começa com "ssh-ed25519 ...")

# 3. Conecte-se ao servidor E2
ssh SEU_USUARIO@IP_DA_MAQUINA

# 4. No servidor, adicione a chave
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDM6NB97PhPWmjbJi/mYfR7FvAQfarzBZJ5tOVoh5BPr github-actions-deploy" >> ~/.ssh/authorized_keys

# 5. Ajuste permissões
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

**Opção C: Via Pipe (uma linha)**

```bash
cat ~/.ssh/gcp_deploy_key.pub | ssh SEU_USUARIO@IP_DA_MAQUINA "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

#### **PASSO 3: Testar a Nova Chave**

```bash
# No seu computador, teste a conexão com a nova chave
ssh -i ~/.ssh/gcp_deploy_key SEU_USUARIO@IP_DA_MAQUINA "echo 'SSH OK!'"

# Se aparecer "SSH OK!", está funcionando! ✅
```

Se pedir senha ou der erro, volte ao PASSO 2 e verifique se a chave pública foi adicionada corretamente.

#### **PASSO 4: Copiar Chave PRIVADA para o GitHub**

```bash
# Ver conteúdo da chave PRIVADA
cat ~/.ssh/gcp_deploy_key

# Copie TODO o conteúdo, incluindo:
# -----BEGIN OPENSSH PRIVATE KEY-----
# [várias linhas de código]
# -----END OPENSSH PRIVATE KEY-----
```

**🚨 ATENÇÃO:** 
- Copie **TUDO**, desde `-----BEGIN` até `-----END`
- Não deixe espaços extras no início ou fim
- Não modifique nenhum caractere

**✅ Resultado:** Chave privada pronta para colar no GitHub Secret

---

## 📝 Resumo Visual

```
┌─────────────────────────────────────────────────────────────┐
│ No seu computador local:                                     │
│                                                              │
│ 1. ssh-keygen -t ed25519 -f ~/.ssh/gcp_deploy_key          │
│    ↓                                                         │
│    Gera: gcp_deploy_key (privada) + gcp_deploy_key.pub     │
│                                                              │
│ 2. cat ~/.ssh/gcp_deploy_key.pub                           │
│    ↓                                                         │
│    Copiar para servidor E2 (~/.ssh/authorized_keys)        │
│                                                              │
│ 3. cat ~/.ssh/gcp_deploy_key                               │
│    ↓                                                         │
│    Copiar para GitHub Secret (GCP_SSH_KEY)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Configurar Secrets no GitHub

Agora que você tem todas as informações, configure os secrets:

### 1. Acesse o Repositório no GitHub

```
https://github.com/SEU_USUARIO/orkestrai-api
```

### 2. Vá em Settings

```
Repositório → Settings → Secrets and variables → Actions
```

### 3. Adicione Cada Secret

Clique em **"New repository secret"** e adicione:

#### Secret 1: GCP_HOST
```
Name: GCP_HOST
Value: 34.123.45.67  (seu IP)
```

#### Secret 2: GCP_USERNAME
```
Name: GCP_USERNAME
Value: joao  (seu usuário)
```

#### Secret 3: GCP_SSH_KEY
```
Name: GCP_SSH_KEY
Value: [Cole aqui TODO o conteúdo da chave privada]
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
[... várias linhas ...]
-----END OPENSSH PRIVATE KEY-----
```

#### Secret 4: GCP_SSH_PORT (Opcional)
```
Name: GCP_SSH_PORT
Value: 22
```
(Só adicione se usar porta diferente de 22)

---

## ✅ Checklist Final

Antes de fazer deploy, verifique:

- [ ] **GCP_HOST**: Você consegue fazer `ping IP_DA_MAQUINA`?
- [ ] **GCP_USERNAME**: Você consegue `ssh USUARIO@IP`?
- [ ] **GCP_SSH_KEY**: Teste funcionou com `ssh -i ~/.ssh/gcp_deploy_key USUARIO@IP`?
- [ ] **Secrets configurados** no GitHub (Settings → Secrets)?
- [ ] **Chave pública** está em `~/.ssh/authorized_keys` no servidor?

---

## 🧪 Testar Configuração

### Teste 1: Conexão SSH Manual

```bash
# No seu computador
ssh -i ~/.ssh/gcp_deploy_key SEU_USUARIO@SEU_IP "echo 'Conexão OK!'"
```

**Esperado:** Deve mostrar "Conexão OK!" sem pedir senha

### Teste 2: Verificar Chave no Servidor

```bash
# Conecte-se ao servidor
ssh SEU_USUARIO@SEU_IP

# Verifique se a chave está lá
cat ~/.ssh/authorized_keys | grep "github-actions-deploy"
```

**Esperado:** Deve mostrar a chave pública

### Teste 3: Workflow Manual

1. Vá em **Actions** no GitHub
2. Selecione **"Deploy to Google Cloud E2"**
3. Clique em **"Run workflow"**
4. Acompanhe os logs

**Esperado:** Deploy deve começar e completar sem erros

---

## 🆘 Problemas Comuns

### ❌ "Permission denied (publickey)"

**Causa:** Chave pública não está no servidor ou permissões incorretas

**Solução:**
```bash
# No servidor E2
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
cat ~/.ssh/authorized_keys  # Verificar se a chave está lá
```

### ❌ "Host key verification failed"

**Causa:** Primeira conexão, host não conhecido

**Solução:**
```bash
# Conectar uma vez manualmente
ssh -i ~/.ssh/gcp_deploy_key SEU_USUARIO@SEU_IP
# Digite "yes" quando perguntar
```

### ❌ "Too many authentication failures"

**Causa:** Muitas chaves SSH tentando

**Solução:**
```bash
# Usar apenas a chave específica
ssh -o IdentitiesOnly=yes -i ~/.ssh/gcp_deploy_key SEU_USUARIO@SEU_IP
```

### ❌ "Connection timed out"

**Causa:** Firewall bloqueando ou IP errado

**Solução:**
```bash
# Verificar firewall GCP permite SSH (porta 22)
gcloud compute firewall-rules list | grep ssh

# Testar conectividade
telnet SEU_IP 22
```

---

## 📚 Exemplo Completo Real

```bash
# === MEU EXEMPLO ===
# Máquina E2: 34.56.78.90
# Usuário: ignitor
# 

# 1. Gerar chave
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/gcp_deploy_key

# 2. Copiar chave pública
ssh-copy-id -i ~/.ssh/gcp_deploy_key.pub ignitor@34.56.78.90

# 3. Testar
ssh -i ~/.ssh/gcp_deploy_key ignitor@34.56.78.90 "echo 'Funciona!'"

# 4. Copiar chave privada
cat ~/.ssh/gcp_deploy_key
# [Copiar TODO o output]

# 5. Adicionar secrets no GitHub:
# GCP_HOST = 34.56.78.90
# GCP_USERNAME = ignitor
# GCP_SSH_KEY = [chave privada copiada]
```

---

## 🎯 Próximos Passos

Depois de configurar os secrets:

1. ✅ Commit suas mudanças
2. ✅ Push para branch main
3. ✅ Acompanhe em Actions → Deploy to Google Cloud E2
4. ✅ Acesse http://SEU_IP:8001/docs

---

**Precisa de mais ajuda?**
- Guia completo: `docs/DEPLOY_SETUP.md`
- FAQ: `docs/FAQ_DEPLOY.md`
- Checklist: `CHECKLIST_DEPLOY.md`

