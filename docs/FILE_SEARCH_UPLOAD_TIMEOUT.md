# File Search Upload - Timeout e Processamento

## ⏱️ Timeout Configurado

O sistema está configurado com:

- **Timeout máximo**: 10 minutos (120 tentativas × 5 segundos)
- **Intervalo entre verificações**: 5 segundos (conforme documentação do Google)
- **Mensagem de erro**: Informa o tempo decorrido e sugere tentar novamente ou usar arquivo menor

## 📋 Processo de Upload

### 1. Upload e Importação

O upload segue o padrão da [documentação oficial do Google](https://ai.google.dev/gemini-api/docs/file-search):

```python
# Upload and import directly
operation = client.file_search_stores.upload_to_file_search_store(
    file=file_content,
    file_search_store_name=store_name,
    config=config
)

# Wait until import is complete
while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)  # Pass operation object directly
```

### 2. Por que pode demorar?

O Google File Search processa arquivos em várias etapas:

1. **Upload**: Envio do arquivo para o Google
2. **Divisão (Chunking)**: Arquivo é dividido em partes menores
3. **Embedding**: Cada parte é convertida em embeddings
4. **Indexação**: Embeddings são indexados para busca rápida
5. **Armazenamento**: Dados são armazenados no File Search Store

**Tempo estimado por tamanho:**
- Arquivos pequenos (< 1 MB): 10-30 segundos
- Arquivos médios (1-10 MB): 30-120 segundos
- Arquivos grandes (10-100 MB): 2-10 minutos

## 🔧 Solução de Problemas

### Erro: "Operation timed out after 10 minutes"

**Possíveis causas:**
1. Arquivo muito grande (> 50 MB)
2. Arquivo com formato complexo (muitas páginas, imagens, etc.)
3. Problemas temporários na API do Google
4. Limite de quota excedido

**Soluções:**
1. **Dividir arquivo grande**: Divida arquivos grandes em partes menores
2. **Tentar novamente**: O processamento pode ter sido interrompido temporariamente
3. **Verificar quota**: Verifique se você não excedeu os limites do Google
4. **Usar arquivo menor**: Para testes, use arquivos menores (< 10 MB)

### Como verificar o progresso

Os logs mostram o progresso:

```
INFO: Waiting for file import to complete...
DEBUG: Operation status check 1/120, done: False
DEBUG: Operation status check 2/120, done: False
...
INFO: Operation completed after 45 seconds
```

## 📊 Limites do Google

Conforme a [documentação oficial](https://ai.google.dev/gemini-api/docs/file-search):

- **Tamanho máximo por arquivo**: 100 MB
- **Tamanho total do projeto** (baseado no nível):
  - **Sem custo**: 1 GB
  - **Nível 1**: 10 GB
  - **Nível 2**: 100 GB
  - **Nível 3**: 1 TB
- **Recomendação**: Limite cada store a menos de 20 GB para latências ideais

## 💡 Dicas de Performance

1. **Arquivos menores são mais rápidos**: Divida documentos grandes em partes
2. **Formatos simples são mais rápidos**: TXT, MD são mais rápidos que PDFs complexos
3. **Evite muitos arquivos simultâneos**: Processe um arquivo por vez
4. **Use chunking config para controle**: Configure `chunking_config` se necessário

## 🔄 Processamento Assíncrono (Futuro)

Para arquivos muito grandes, considere implementar processamento assíncrono:

1. Iniciar upload e retornar imediatamente
2. Processar em background
3. Notificar usuário quando completo
4. Permitir verificação de status

Isso melhora a experiência do usuário para arquivos grandes.

