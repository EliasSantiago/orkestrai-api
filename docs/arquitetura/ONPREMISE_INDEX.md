# 📚 Índice Completo: Documentação On-Premise

Guia de navegação para toda documentação sobre uso de modelos on-premise.

## 🚀 **Comece Aqui**

### **1. Guia Rápido** (Recomendado para Iniciantes)
📄 **[ONPREMISE_QUICK_CREATE_AGENT.md](ONPREMISE_QUICK_CREATE_AGENT.md)**
- ⏱️ Tempo: 10 minutos
- 🎯 Objetivo: Criar seu primeiro agente on-premise
- 📝 Conteúdo: Passo a passo com exemplos JSON
- 👥 Para: Desenvolvedores iniciantes

**O que você aprenderá:**
- Como configurar o `.env`
- Como criar agentes com modelos on-premise
- 5 exemplos práticos prontos para usar
- Troubleshooting de problemas comuns

---

## 📖 **Documentação Detalhada**

### **2. Modelos Disponíveis**
📄 **[ONPREMISE_MODELS_AVAILABLE.md](ONPREMISE_MODELS_AVAILABLE.md)**
- ⏱️ Tempo: 15 minutos
- 🎯 Objetivo: Conhecer todos os 20 modelos disponíveis
- 📝 Conteúdo: Lista completa, comparações, recomendações
- 👥 Para: Desenvolvedores escolhendo modelos

**O que você aprenderá:**
- Lista dos 20 modelos on-premise
- Qual modelo usar para cada caso
- Comparações de tamanho e velocidade
- Tipos de quantização (FP16, Q4_K_M)

### **3. Convenções de Nomenclatura**
📄 **[ONPREMISE_MODEL_NAMING_CONVENTIONS.md](ONPREMISE_MODEL_NAMING_CONVENTIONS.md)**
- ⏱️ Tempo: 10 minutos
- 🎯 Objetivo: Entender como nomear modelos
- 📝 Conteúdo: 3 formas de usar, comparações, boas práticas
- 👥 Para: Desenvolvedores em ambientes complexos

**O que você aprenderá:**
- Nome real vs prefixos (`onpremise-`, `local-`)
- Quando usar cada formato
- Como o sistema detecta providers
- Boas práticas de nomenclatura

### **4. Resumo Técnico**
📄 **[RESUMO_AJUSTES_ONPREMISE.md](RESUMO_AJUSTES_ONPREMISE.md)**
- ⏱️ Tempo: 15 minutos
- 🎯 Objetivo: Entender mudanças técnicas
- 📝 Conteúdo: Detalhes de implementação
- 👥 Para: Desenvolvedores técnicos, revisores de código

**O que você aprenderá:**
- Mudanças no código
- Razão de cada ajuste
- Arquivos modificados
- Estatísticas do projeto

### **5. Resumo Executivo**
📄 **[ONPREMISE_FINAL_SUMMARY.md](ONPREMISE_FINAL_SUMMARY.md)**
- ⏱️ Tempo: 5 minutos
- 🎯 Objetivo: Visão geral completa
- 📝 Conteúdo: Resumo de tudo implementado
- 👥 Para: Gerentes, líderes técnicos

**O que você aprenderá:**
- Status do projeto
- Conquistas alcançadas
- Checklist de validação
- Próximos passos

---

## 🔧 **Configuração e Setup**

### **6. Configuração de Endpoint**
📄 **[ONPREMISE_ENDPOINT_CONFIG.md](ONPREMISE_ENDPOINT_CONFIG.md)**
- ⏱️ Tempo: 5 minutos
- 🎯 Objetivo: Configurar endpoints customizados
- 📝 Conteúdo: Como usar `ONPREMISE_CHAT_ENDPOINT`
- 👥 Para: DevOps, administradores

### **7. Quick Start**
📄 **[ONPREMISE_QUICK_START.md](ONPREMISE_QUICK_START.md)**
- ⏱️ Tempo: 5 minutos
- 🎯 Objetivo: Setup rápido em 5 minutos
- 📝 Conteúdo: Passos mínimos para começar
- 👥 Para: Todos

### **8. Setup do Provider**
📄 **[ONPREMISE_PROVIDER_SETUP.md](ONPREMISE_PROVIDER_SETUP.md)**
- ⏱️ Tempo: 20 minutos
- 🎯 Objetivo: Configuração completa
- 📝 Conteúdo: Setup detalhado com OAuth
- 👥 Para: Administradores de sistema

---

## 🧪 **Testes e Validação**

### **9. Script: Test Model Routing**
📄 **[scripts/test_model_routing.py](../scripts/test_model_routing.py)**
- ⏱️ Tempo: 1 minuto
- 🎯 Objetivo: Validar roteamento de modelos
- 📝 Conteúdo: Testa 16 modelos entre providers
- 👥 Para: Desenvolvedores, QA

**Como executar:**
```bash
python scripts/test_model_routing.py
```

### **10. Script: Test On-Premise Complete**
📄 **[scripts/test_onpremise_with_real_models.py](../scripts/test_onpremise_with_real_models.py)**
- ⏱️ Tempo: 2 minutos
- 🎯 Objetivo: Testes completos do provider
- 📝 Conteúdo: 4 testes (OAuth, models, chat, detecção)
- 👥 Para: Desenvolvedores, QA

**Como executar:**
```bash
python scripts/test_onpremise_with_real_models.py
```

---

## 📚 **Documentação Adicional**

### **11. OAuth Setup**
📄 **[ONPREMISE_OAUTH_SETUP.md](ONPREMISE_OAUTH_SETUP.md)**
- OAuth client_credentials
- Configuração de credenciais
- Troubleshooting OAuth

### **12. Cheat Sheet**
📄 **[ONPREMISE_CHEAT_SHEET.md](ONPREMISE_CHEAT_SHEET.md)**
- Comandos rápidos
- Exemplos comuns
- Referência rápida

### **13. Explicação de Modelos**
📄 **[ONPREMISE_MODELS_EXPLANATION.md](ONPREMISE_MODELS_EXPLANATION.md)**
- Detalhes técnicos dos modelos
- Diferenças entre versões
- Casos de uso específicos

---

## 🎯 **Fluxo de Aprendizado Recomendado**

### **Para Iniciantes:**
1. 📄 [ONPREMISE_QUICK_START.md](ONPREMISE_QUICK_START.md) *(5 min)*
2. 📄 [ONPREMISE_QUICK_CREATE_AGENT.md](ONPREMISE_QUICK_CREATE_AGENT.md) *(10 min)*
3. 📄 [ONPREMISE_MODELS_AVAILABLE.md](ONPREMISE_MODELS_AVAILABLE.md) *(15 min)*
4. 🧪 Executar `test_model_routing.py` *(1 min)*

**Total: ~30 minutos**

### **Para Desenvolvedores Experientes:**
1. 📄 [ONPREMISE_QUICK_CREATE_AGENT.md](ONPREMISE_QUICK_CREATE_AGENT.md) *(10 min)*
2. 📄 [ONPREMISE_MODEL_NAMING_CONVENTIONS.md](ONPREMISE_MODEL_NAMING_CONVENTIONS.md) *(10 min)*
3. 📄 [RESUMO_AJUSTES_ONPREMISE.md](RESUMO_AJUSTES_ONPREMISE.md) *(15 min)*
4. 🧪 Executar ambos os scripts de teste *(3 min)*

**Total: ~40 minutos**

### **Para Gerentes/Líderes:**
1. 📄 [ONPREMISE_FINAL_SUMMARY.md](ONPREMISE_FINAL_SUMMARY.md) *(5 min)*
2. 📄 [ONPREMISE_MODELS_AVAILABLE.md](ONPREMISE_MODELS_AVAILABLE.md) - apenas tabelas *(5 min)*

**Total: ~10 minutos**

---

## 🔍 **Busca Rápida**

### **Preciso de:**

| Busco | Veja |
|-------|------|
| **Criar meu primeiro agente** | [ONPREMISE_QUICK_CREATE_AGENT.md](ONPREMISE_QUICK_CREATE_AGENT.md) |
| **Lista de modelos** | [ONPREMISE_MODELS_AVAILABLE.md](ONPREMISE_MODELS_AVAILABLE.md) |
| **Usar prefixo onpremise-** | [ONPREMISE_MODEL_NAMING_CONVENTIONS.md](ONPREMISE_MODEL_NAMING_CONVENTIONS.md) |
| **Configurar OAuth** | [ONPREMISE_OAUTH_SETUP.md](ONPREMISE_OAUTH_SETUP.md) |
| **Resolver erro de roteamento** | [ONPREMISE_QUICK_CREATE_AGENT.md](ONPREMISE_QUICK_CREATE_AGENT.md#troubleshooting) |
| **Entender mudanças no código** | [RESUMO_AJUSTES_ONPREMISE.md](RESUMO_AJUSTES_ONPREMISE.md) |
| **Testar roteamento** | `scripts/test_model_routing.py` |
| **Visão geral do projeto** | [ONPREMISE_FINAL_SUMMARY.md](ONPREMISE_FINAL_SUMMARY.md) |

---

## 📊 **Estatísticas da Documentação**

| Métrica | Valor |
|---------|-------|
| **Documentos Criados** | 13 |
| **Scripts de Teste** | 2 |
| **Exemplos JSON** | 15+ |
| **Modelos Documentados** | 20 |
| **Tempo Total de Leitura** | ~2 horas |
| **Casos de Uso** | 10+ |

---

## 🎓 **Recursos Externos**

### **APIs e Referências:**
- 🌐 [API On-Premise](https://apidesenv.go.gov.br/ia/modelos-linguagem-natural/v2.0/)
- 📖 [Swagger UI Local](http://localhost:8001/docs)
- 🔧 [Ollama Documentation](https://ollama.ai/docs)

### **Modelos e Frameworks:**
- 🤖 [Qwen Models](https://huggingface.co/Qwen)
- 🦙 [Llama Models](https://huggingface.co/meta-llama)
- 💎 [Gemma Models](https://huggingface.co/google/gemma)

---

## 🏗️ **Arquitetura da Aplicação**

### **14. Guia de Arquitetura** (Completo)
📄 **[ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)**
- ⏱️ Tempo: 30 minutos
- 🎯 Objetivo: Entender a arquitetura completa
- 📝 Conteúdo: Clean Architecture, DDD, Fluxos
- 👥 Para: Desenvolvedores, arquitetos

**O que você aprenderá:**
- Estrutura de camadas (API, Application, Domain, Infrastructure)
- Fluxo completo de uma requisição
- Como adicionar novos endpoints
- Exemplos práticos completos

### **15. Guia Rápido: Adicionar Recurso**
📄 **[ADD_NEW_FEATURE_QUICK_GUIDE.md](ADD_NEW_FEATURE_QUICK_GUIDE.md)**
- ⏱️ Tempo: 10 minutos
- 🎯 Objetivo: Passo a passo para novos recursos
- 📝 Conteúdo: Tutorial prático com exemplo
- 👥 Para: Desenvolvedores

**O que você aprenderá:**
- Ordem exata de criação de arquivos
- Templates prontos para usar
- Checklist completo
- Troubleshooting

### **16. Resumo Visual da Arquitetura**
📄 **[ARCHITECTURE_VISUAL_SUMMARY.md](ARCHITECTURE_VISUAL_SUMMARY.md)**
- ⏱️ Tempo: 15 minutos
- 🎯 Objetivo: Diagramas e visualizações
- 📝 Conteúdo: Fluxos visuais, diagramas ASCII
- 👥 Para: Visual learners

**O que você aprenderá:**
- Diagramas de fluxo
- Estrutura visual de pastas
- Entity vs Model
- Princípios SOLID aplicados

---

## 🆘 **Suporte e Ajuda**

### **Problemas Comuns:**

1. **Modelo vai para Ollama em vez de OnPremise**
   - Solução: Reiniciar servidor após mudanças
   - Ver: [ONPREMISE_QUICK_CREATE_AGENT.md](ONPREMISE_QUICK_CREATE_AGENT.md#troubleshooting)

2. **OAuth falha**
   - Solução: Verificar credenciais no `.env`
   - Ver: [ONPREMISE_OAUTH_SETUP.md](ONPREMISE_OAUTH_SETUP.md)

3. **Modelo não encontrado**
   - Solução: Verificar lista de modelos disponíveis
   - Ver: [ONPREMISE_MODELS_AVAILABLE.md](ONPREMISE_MODELS_AVAILABLE.md)

4. **Erro 404 no chat**
   - Solução: Verificar `ONPREMISE_CHAT_ENDPOINT`
   - Ver: [ONPREMISE_ENDPOINT_CONFIG.md](ONPREMISE_ENDPOINT_CONFIG.md)

### **Comandos Úteis:**

```bash
# Testar roteamento
python scripts/test_model_routing.py

# Testar on-premise completo
python scripts/test_onpremise_with_real_models.py

# Reiniciar servidor
pkill -f uvicorn
python -m uvicorn src.api.main:app --reload --port 8001

# Ver logs em tempo real
tail -f logs/application.log
```

---

## ✅ **Checklist de Uso**

Antes de começar, certifique-se:

- [ ] ✅ `.env` configurado com credenciais on-premise
- [ ] ✅ Servidor rodando (`http://localhost:8001`)
- [ ] ✅ OAuth funcionando (testar com script)
- [ ] ✅ Conhece os modelos disponíveis
- [ ] ✅ Sabe qual formato de nomenclatura usar
- [ ] ✅ Leu o guia rápido

---

## 🎉 **Conclusão**

Esta documentação cobre **100%** do que você precisa para usar modelos on-premise:

✅ **Setup** - Como configurar  
✅ **Uso** - Como criar agentes  
✅ **Modelos** - Quais estão disponíveis  
✅ **Nomenclatura** - Como nomear  
✅ **Testes** - Como validar  
✅ **Troubleshooting** - Como resolver problemas  

**Comece agora:** [ONPREMISE_QUICK_CREATE_AGENT.md](ONPREMISE_QUICK_CREATE_AGENT.md) 🚀

---

**Última atualização:** 11/11/2025  
**Status:** ✅ Completo e validado  
**Versão:** 1.0
