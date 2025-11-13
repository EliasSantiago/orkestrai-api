# 📚 Documentação de Arquitetura - Início Aqui

## 🎯 **Começe por aqui!**

Você está no lugar certo se quer entender:
- ✅ Como a aplicação está organizada
- ✅ Como adicionar novos recursos/endpoints
- ✅ Qual arquivo modificar para cada mudança

---

## 🚀 **Escolha seu caminho:**

### **🔰 Iniciante: "Preciso adicionar um endpoint"**

👉 **Leia:** [ADD_NEW_FEATURE_QUICK_GUIDE.md](ADD_NEW_FEATURE_QUICK_GUIDE.md)  
⏱️ **Tempo:** 10 minutos  
📝 **Conteúdo:** Passo a passo com exemplo completo

### **🏗️ Desenvolvedor: "Quero entender a arquitetura"**

👉 **Leia:** [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)  
⏱️ **Tempo:** 30 minutos  
📝 **Conteúdo:** Clean Architecture, DDD, princípios SOLID

### **🎨 Visual: "Prefiro diagramas e exemplos visuais"**

👉 **Leia:** [ARCHITECTURE_VISUAL_SUMMARY.md](ARCHITECTURE_VISUAL_SUMMARY.md)  
⏱️ **Tempo:** 15 minutos  
📝 **Conteúdo:** Fluxos visuais, diagramas ASCII

---

## 📋 **Resumo Ultra-Rápido**

### **Estrutura em 4 Camadas:**

```
1. API Layer          → Rotas HTTP (FastAPI)
2. Application Layer  → Casos de uso (lógica de app)
3. Domain Layer       → Entidades e regras de negócio
4. Infrastructure     → Banco de dados, APIs externas
```

### **Para adicionar um novo endpoint:**

```
1. Domain       → Criar/atualizar Entity
2. Infrastructure → Criar Migration + Repository
3. Application  → Criar Use Case
4. API          → Criar Schema + Route
5. Testar       → Reiniciar + testar
```

### **Arquivos principais:**

| Preciso | Arquivo |
|---------|---------|
| Nova rota | `src/api/*_routes.py` |
| Validação de entrada | `src/api/schemas.py` |
| Lógica de negócio | `src/application/use_cases/` |
| Mudança no banco | `src/models.py` + migration |
| Config | `src/config.py` |

---

## 📚 **Documentação Completa**

### **Arquitetura:**
- [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - Guia completo
- [ADD_NEW_FEATURE_QUICK_GUIDE.md](ADD_NEW_FEATURE_QUICK_GUIDE.md) - Guia rápido
- [ARCHITECTURE_VISUAL_SUMMARY.md](ARCHITECTURE_VISUAL_SUMMARY.md) - Diagramas visuais

### **On-Premise:**
- [ONPREMISE_INDEX.md](ONPREMISE_INDEX.md) - Índice completo
- [ONPREMISE_QUICK_CREATE_AGENT.md](ONPREMISE_QUICK_CREATE_AGENT.md) - Criar agentes
- [ONPREMISE_MODELS_AVAILABLE.md](ONPREMISE_MODELS_AVAILABLE.md) - 20 modelos
- [ONPREMISE_MODEL_NAMING_CONVENTIONS.md](ONPREMISE_MODEL_NAMING_CONVENTIONS.md) - Nomenclatura

---

## 🎯 **Exemplos Práticos**

### **Exemplo 1: Adicionar campo "is_favorite" aos agentes**

```bash
# 1. Domain
src/domain/entities/agent.py → adicionar: is_favorite: bool

# 2. Infrastructure
src/models.py → adicionar: is_favorite = Column(Boolean)
alembic revision -m "add_is_favorite"
alembic upgrade head

# 3. Application
src/application/use_cases/agents/toggle_favorite.py → criar

# 4. API
src/api/schemas.py → adicionar ao AgentResponse
src/api/agent_routes.py → adicionar rota
src/api/di.py → adicionar factory

# 5. Testar
curl -X POST /api/agents/1/favorite
```

### **Exemplo 2: Criar endpoint para listar modelos**

```bash
# 1. Application
src/application/use_cases/models/list_models.py → criar

# 2. API
src/api/schemas.py → criar ModelsListResponse
src/api/models_routes.py → criar rota
src/api/main.py → registrar router

# 3. Testar
curl -X GET /api/models
```

---

## 🔍 **FAQ Rápido**

**P: Onde adiciono uma nova rota?**  
R: `src/api/*_routes.py` + registrar em `main.py`

**P: Onde valido dados de entrada?**  
R: `src/api/schemas.py` (Pydantic)

**P: Onde fica a lógica de negócio?**  
R: `src/application/use_cases/` e `src/domain/`

**P: Como adiciono um campo no banco?**  
R: `src/models.py` + migration (alembic)

**P: Onde configuro variáveis de ambiente?**  
R: `.env` e `src/config.py`

**P: Como testo meu endpoint?**  
R: Swagger UI em `http://localhost:8001/docs`

---

## 🛠️ **Comandos Úteis**

```bash
# Criar migration
alembic revision --autogenerate -m "descrição"

# Aplicar migration
alembic upgrade head

# Reverter migration
alembic downgrade -1

# Reiniciar servidor
./scripts/start_backend.sh

# Testar roteamento de modelos
python scripts/test_model_routing.py
```

---

## 📊 **Fluxo Visual Simplificado**

```
Cliente HTTP
    ↓
API Layer (routes.py)
    ↓
Application Layer (use_cases/)
    ↓
Domain Layer (entities/, repositories/)
    ↓
Infrastructure Layer (database/)
    ↓
PostgreSQL
```

---

## ✅ **Próximos Passos**

1. 📖 Leia o guia que melhor se encaixa no seu perfil
2. 🧪 Teste os exemplos fornecidos
3. 🚀 Adicione seu próprio recurso seguindo o guia
4. 💬 Consulte a documentação quando tiver dúvidas

---

## 🆘 **Precisa de Ajuda?**

- **Arquitetura:** Veja [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)
- **Adicionar recurso:** Veja [ADD_NEW_FEATURE_QUICK_GUIDE.md](ADD_NEW_FEATURE_QUICK_GUIDE.md)
- **Modelos on-premise:** Veja [ONPREMISE_INDEX.md](ONPREMISE_INDEX.md)

---

**Boa codificação! 🚀**

