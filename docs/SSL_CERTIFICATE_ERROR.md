# Resolvendo Erros de Certificado SSL

Este documento explica como resolver erros de certificado SSL ao usar provedores LLM.

## 🔴 Erro Comum

```
CERTIFICATE_VERIFY_FAILED: certificate verify failed: self-signed certificate in certificate chain
```

Este erro ocorre quando:
- Você está em um ambiente corporativo com proxy/firewall
- O certificado SSL é autoassinado
- Há um interceptador de SSL (como em ambientes corporativos)

## ✅ Solução Rápida (Desenvolvimento)

Para ambientes de desenvolvimento, você pode desabilitar a verificação SSL adicionando no `.env`:

```env
VERIFY_SSL=false
```

**⚠️ ATENÇÃO:** Isso desabilita a verificação SSL e é **inseguro**. Use apenas em desenvolvimento!

## 🔒 Solução Segura (Produção)

### Opção 1: Adicionar Certificado ao Sistema

1. Obtenha o certificado do seu ambiente corporativo
2. Adicione ao sistema:

```bash
# Ubuntu/Debian
sudo cp certificado.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

### Opção 2: Configurar Variáveis de Ambiente

Configure as variáveis de proxy se necessário:

```env
HTTP_PROXY=http://proxy.corporativo.com:8080
HTTPS_PROXY=http://proxy.corporativo.com:8080
NO_PROXY=localhost,127.0.0.1
```

### Opção 3: Usar Certificado Específico

Se você tem um certificado específico, pode configurar:

```python
# Em um provider customizado
import ssl
import certifi

ssl_context = ssl.create_default_context(cafile="/caminho/para/certificado.crt")
```

## 📝 Mensagens de Erro Melhoradas

A aplicação agora fornece mensagens de erro mais claras:

### Erro de Certificado SSL
```
Erro de certificado SSL ao conectar à API OpenAI. 
Isso geralmente ocorre em ambientes corporativos com certificados autoassinados. 
Para resolver, adicione no .env: VERIFY_SSL=false 
(⚠️ ATENÇÃO: Isso desabilita verificação SSL e é inseguro - use apenas em desenvolvimento)
```

### Erro de Conexão
```
Erro de conexão com a API OpenAI. 
Verifique sua conexão com a internet e se a API OpenAI está acessível. 
Se estiver atrás de um proxy corporativo, pode ser necessário configurar variáveis de ambiente HTTP_PROXY/HTTPS_PROXY.
```

### Erro de Autenticação
```
Erro de autenticação com a API OpenAI. 
Verifique se a OPENAI_API_KEY está configurada corretamente no arquivo .env
```

## 🔍 Verificando a Configuração

1. Verifique se `VERIFY_SSL` está no `.env`:
   ```bash
   grep VERIFY_SSL .env
   ```

2. Reinicie a aplicação após alterar o `.env`

3. Teste novamente a requisição

## 🛡️ Segurança

- **Nunca** desabilite SSL em produção
- **Sempre** use certificados válidos em produção
- **Considere** usar um proxy reverso com SSL válido
- **Monitore** logs para detectar problemas de SSL

## 📚 Referências

- [Python SSL Documentation](https://docs.python.org/3/library/ssl.html)
- [httpx SSL Configuration](https://www.python-httpx.org/advanced/ssl/)
- [OpenAI API Troubleshooting](https://platform.openai.com/docs/guides/error-codes)

