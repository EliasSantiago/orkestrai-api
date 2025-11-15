# 🔐 MCP_ENCRYPTION_KEY - Guia de Configuração

## O que é?

A `MCP_ENCRYPTION_KEY` é uma chave de criptografia usada para **criptografar as credenciais do Notion** (e outras integrações MCP) antes de armazená-las no banco de dados.

## Para que serve?

Quando um usuário conecta sua conta do Notion, a API key é armazenada no banco de dados. Para segurança, essa chave é **criptografada** antes de ser salva. A `MCP_ENCRYPTION_KEY` é usada para:

1. **Criptografar** credenciais antes de salvar no banco
2. **Descriptografar** credenciais quando necessário para usar a API do Notion

## Por que é importante?

- 🔒 **Segurança**: Protege as credenciais mesmo se o banco de dados for comprometido
- 🛡️ **Privacidade**: Ninguém pode ver as API keys dos usuários sem a chave
- ✅ **Boas práticas**: Segue padrões de segurança empresariais

## Como gerar a chave?

### Opção 1: Usando Python (Recomendado)

```bash
python3 -c "from cryptography.fernet import Fernet; key = Fernet.generate_key(); print('MCP_ENCRYPTION_KEY=' + key.decode())"
```

Isso gerará algo como:
```
MCP_ENCRYPTION_KEY=YWuBbmlz5CP1NVUXWUs1UVqlqeLmoUfUQnZKWEX8lMA=
```

### Opção 2: Usando Python interativo

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

### Opção 3: Script dedicado

Crie um arquivo `generate_key.py`:
```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(f"MCP_ENCRYPTION_KEY={key.decode()}")
```

Execute:
```bash
python3 generate_key.py
```

## Como configurar?

### 1. Adicione no arquivo `.env`

Abra ou crie o arquivo `.env` na raiz do projeto e adicione:

```bash
# Chave de criptografia para credenciais MCP
# Gere uma nova chave usando: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
MCP_ENCRYPTION_KEY=YWuBbmlz5CP1NVUXWUs1UVqlqeLmoUfUQnZKWEX8lMA=
```

**⚠️ IMPORTANTE**: Substitua pelo valor gerado por você!

### 2. Verifique se está funcionando

Ao iniciar a aplicação, você não deve ver o aviso:
```
⚠️  WARNING: MCP_ENCRYPTION_KEY not set. Generated temporary key: ...
```

Se não aparecer o aviso, está configurado corretamente!

## ⚠️ Avisos Importantes

### Em Desenvolvimento

- Se você **não** configurar a chave, o sistema gerará uma temporária
- ⚠️ **Atenção**: Se você reiniciar a aplicação, uma nova chave será gerada
- ⚠️ **Problema**: Credenciais criptografadas com a chave antiga não poderão ser descriptografadas!

### Em Produção

- ✅ **OBRIGATÓRIO**: Sempre configure `MCP_ENCRYPTION_KEY` em produção
- ✅ **Segurança**: Use uma chave forte e única
- ✅ **Backup**: Guarde a chave em local seguro (gerenciador de senhas, etc.)
- ✅ **Rotação**: Considere rotacionar a chave periodicamente

## 🔄 O que acontece se eu mudar a chave?

Se você mudar `MCP_ENCRYPTION_KEY`:

1. ✅ **Novas conexões**: Funcionarão normalmente
2. ❌ **Conexões antigas**: Não poderão ser descriptografadas
3. 🔧 **Solução**: Usuários precisarão reconectar suas contas Notion

## 📋 Checklist

- [ ] Gerei uma chave usando um dos métodos acima
- [ ] Adicionei `MCP_ENCRYPTION_KEY=...` no arquivo `.env`
- [ ] Verifiquei que não há avisos ao iniciar a aplicação
- [ ] Guardei a chave em local seguro (produção)
- [ ] Adicionei `.env` no `.gitignore` (se ainda não estiver)

## 🔍 Verificação

Para verificar se está configurado corretamente:

```bash
# Verifique se a variável está no .env
grep MCP_ENCRYPTION_KEY .env

# Inicie a aplicação e verifique os logs
# Não deve aparecer o aviso de chave não configurada
```

## 💡 Dica

Se você já tem credenciais salvas e mudou a chave, você pode:

1. **Opção 1**: Reconectar todas as contas Notion
2. **Opção 2**: Usar a chave antiga para descriptografar e re-criptografar com a nova

Para a Opção 2, você precisaria de um script de migração (não incluído por padrão).

## 🆘 Problemas Comuns

### "Failed to decrypt credentials"

**Causa**: A chave de criptografia mudou ou está incorreta.

**Solução**: 
1. Verifique se `MCP_ENCRYPTION_KEY` está correto no `.env`
2. Se mudou, reconecte as contas Notion afetadas

### "MCP_ENCRYPTION_KEY not set"

**Causa**: A variável não está no `.env` ou não está sendo carregada.

**Solução**:
1. Verifique se o arquivo `.env` existe na raiz do projeto
2. Verifique se `python-dotenv` está instalado
3. Reinicie a aplicação após adicionar a chave

