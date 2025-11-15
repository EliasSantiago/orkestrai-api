# 🔒 Checklist de Segurança para Produção

## ✅ Configurações Implementadas

### 1. Variáveis de Ambiente
- [x] Senhas movidas para arquivo `.env`
- [x] Arquivo `.env.example` criado como template
- [x] Variáveis de ambiente configuradas no docker-compose.yml
- [x] Valores padrão definidos para variáveis opcionais

### 2. PostgreSQL
- [x] Senha forte obrigatória via variável de ambiente
- [x] Método de autenticação seguro (scram-sha-256)
- [x] Healthcheck configurado
- [x] Limites de recursos definidos
- [x] Logging configurado com rotação
- [x] Network isolada

### 3. Redis
- [x] Senha obrigatória configurada (requirepass)
- [x] Persistência habilitada (appendonly)
- [x] Limite de memória configurado (512mb)
- [x] Política de eviction configurada (allkeys-lru)
- [x] Healthcheck com autenticação
- [x] Limites de recursos definidos
- [x] Logging configurado com rotação
- [x] Network isolada

### 4. Docker Compose
- [x] Network isolada criada
- [x] Volumes nomeados para facilitar backup
- [x] Restart policy configurada (unless-stopped)
- [x] Logging com rotação de arquivos

## ⚠️ Ações Necessárias ANTES de Colocar em Produção

### 🔐 Segurança de Credenciais
- [ ] **CRÍTICO**: Copiar `.env.example` para `.env` e alterar TODAS as senhas
- [ ] **CRÍTICO**: Gerar senhas fortes e únicas (mínimo 16 caracteres, mistura de maiúsculas, minúsculas, números e símbolos)
- [ ] **CRÍTICO**: Adicionar `.env` ao `.gitignore` (se ainda não estiver)
- [ ] **CRÍTICO**: Nunca commitar o arquivo `.env` no repositório
- [ ] Verificar permissões do arquivo `.env` (chmod 600 recomendado)

### 🌐 Rede e Firewall
- [ ] Considerar remover exposição de portas para o host (usar apenas network interna)
  - Se a aplicação Python estiver na mesma máquina, pode acessar via network interna
  - Se precisar acessar externamente, configurar firewall adequadamente
- [ ] Configurar firewall (UFW/iptables) para restringir acesso às portas expostas
- [ ] Considerar usar reverse proxy (nginx/traefik) ao invés de expor portas diretamente
- [ ] Se possível, usar apenas network interna do Docker (remover `ports:` ou restringir a `127.0.0.1`)

### 🔒 Hardening Adicional
- [ ] Configurar SSL/TLS para PostgreSQL (se acesso externo necessário)
- [ ] Configurar SSL/TLS para Redis (se acesso externo necessário)
- [ ] Revisar e ajustar limites de recursos conforme necessidade real
- [ ] Configurar backups automáticos dos volumes
- [ ] Configurar monitoramento e alertas
- [ ] Revisar logs regularmente

### 📋 Configurações do Sistema
- [ ] Atualizar imagens Docker para versões mais recentes regularmente
- [ ] Configurar atualizações automáticas de segurança do sistema
- [ ] Configurar fail2ban ou similar para proteção contra brute force
- [ ] Revisar permissões de arquivos e diretórios do Docker

### 🔍 Monitoramento
- [ ] Configurar monitoramento de saúde dos containers
- [ ] Configurar alertas para falhas de healthcheck
- [ ] Configurar monitoramento de uso de recursos
- [ ] Configurar logs centralizados (opcional, mas recomendado)

### 💾 Backup e Recuperação
- [ ] Configurar backup automático do volume PostgreSQL
- [ ] Configurar backup automático do volume Redis (se necessário)
- [ ] Testar processo de restauração de backups
- [ ] Documentar procedimento de recuperação de desastre

### 🐍 Integração com Aplicação Python
- [ ] Atualizar strings de conexão na aplicação Python para usar variáveis de ambiente
- [ ] Testar conexão com PostgreSQL usando novas credenciais
- [ ] Testar conexão com Redis usando nova senha
- [ ] Verificar se aplicação Python está na mesma network do Docker (ou configurar acesso adequado)

## 📝 Comandos Úteis

### Gerar senha segura
```bash
# Opção 1: openssl
openssl rand -base64 32

# Opção 2: /dev/urandom
tr -dc 'A-Za-z0-9!@#$%^&*' < /dev/urandom | head -c 32

# Opção 3: pwgen (se instalado)
pwgen -s 32 1
```

### Verificar se .env está no .gitignore
```bash
grep -q "^\.env$" .gitignore && echo "OK" || echo "ADICIONAR .env ao .gitignore"
```

### Configurar permissões do .env
```bash
chmod 600 .env
```

### Testar conexão PostgreSQL
```bash
docker exec -it agents_postgres psql -U agentuser -d agentsdb
```

### Testar conexão Redis
```bash
docker exec -it agents_redis redis-cli -a "sua_senha_aqui" ping
```

### Ver logs dos containers
```bash
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Verificar uso de recursos
```bash
docker stats agents_postgres agents_redis
```

## 🚨 Avisos Importantes

1. **NUNCA** commite o arquivo `.env` no repositório Git
2. **SEMPRE** use senhas fortes e únicas em produção
3. **CONSIDERE** usar um gerenciador de secrets (HashiCorp Vault, AWS Secrets Manager, etc.) para ambientes críticos
4. **REVISE** regularmente as configurações de segurança
5. **MANTENHA** as imagens Docker atualizadas

## 📚 Recursos Adicionais

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [Redis Security](https://redis.io/docs/management/security/)

