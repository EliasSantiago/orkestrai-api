#!/usr/bin/env python3
"""
Script para testar o provedor on-premise com os modelos reais disponíveis.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage
import httpx
from src.config import Config


# Lista de modelos reais disponíveis na API on-premise
AVAILABLE_MODELS = [
    # Modelos de código
    "qwen3-coder:30b",
    
    # Modelos de raciocínio
    "deepseek-r1:14b",
    "deepseek-r1:8b",
    "deepseek-r1:1.5b-qwen-distill-fp16",
    
    # Família Qwen
    "qwen3:30b-a3b-instruct-2507-q4_K_M",
    "qwen3:30b-a3b-instruct-2507-fp16",
    "qwen3:14b",
    "qwen2.5:7b-instruct-fp16",
    "qwen2.5:14b",
    
    # Família Gemma
    "gemma3:27b-it-q4_K_M",
    "gemma3:12b-it-fp16",
    "gemma3:12b-it-q4_K_M",
    "gemma3:12b",
    "gemma3:latest",
    
    # Família Llama
    "llama3.1:8b-instruct-fp16",
    "llama3.1:8b",
    "llama3.2:3b",
    
    # Outros
    "gpt-oss:20b",
    "phi4:14b",
    "nomic-embed-text:latest",
]


async def test_model_detection():
    """Testa se os modelos são detectados corretamente como on-premise."""
    print("=" * 70)
    print("🧪 TESTE 1: Detecção de Modelos")
    print("=" * 70)
    print()
    
    # Modelos que DEVEM ser detectados como on-premise
    onpremise_models = AVAILABLE_MODELS
    
    # Modelos que NÃO DEVEM ser detectados como on-premise
    other_provider_models = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
    ]
    
    print("✅ Testando modelos ON-PREMISE (devem ser aceitos):\n")
    
    correct_detections = 0
    total_onpremise = len(onpremise_models)
    
    for model in onpremise_models:
        provider = LLMFactory.get_provider(model)
        if provider and provider.__class__.__name__ == "OnPremiseProvider":
            print(f"   ✅ {model:45} → OnPremiseProvider")
            correct_detections += 1
        else:
            provider_name = provider.__class__.__name__ if provider else "NENHUM"
            print(f"   ❌ {model:45} → {provider_name} (ERRO!)")
    
    print()
    print(f"📊 Resultado: {correct_detections}/{total_onpremise} detectados corretamente")
    print()
    print("-" * 70)
    print()
    print("❌ Testando modelos de OUTROS PROVEDORES (devem ser rejeitados):\n")
    
    correct_rejections = 0
    total_others = len(other_provider_models)
    
    for model in other_provider_models:
        provider = LLMFactory.get_provider(model)
        provider_name = provider.__class__.__name__ if provider else "NENHUM"
        
        if provider_name != "OnPremiseProvider":
            print(f"   ✅ {model:45} → {provider_name}")
            correct_rejections += 1
        else:
            print(f"   ❌ {model:45} → OnPremiseProvider (ERRO!)")
    
    print()
    print(f"📊 Resultado: {correct_rejections}/{total_others} rejeitados corretamente")
    print()
    
    return correct_detections == total_onpremise and correct_rejections == total_others


async def test_oauth_token():
    """Testa a geração de token OAuth."""
    print("=" * 70)
    print("🧪 TESTE 2: Token OAuth")
    print("=" * 70)
    print()
    
    try:
        from src.core.oauth_token_manager import OAuthTokenManager
        
        oauth_manager = OAuthTokenManager()
        print("🔐 Gerando token OAuth...")
        token = await oauth_manager.get_token()
        
        if token:
            print(f"✅ Token gerado com sucesso!")
            print(f"   Token: {token[:50]}...")
            return True
        else:
            print("❌ Token vazio")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao gerar token: {e}")
        return False


async def test_api_models_endpoint():
    """Testa o endpoint /models da API on-premise."""
    print("=" * 70)
    print("🧪 TESTE 3: Endpoint /models da API")
    print("=" * 70)
    print()
    
    try:
        from src.core.oauth_token_manager import OAuthTokenManager
        
        # Obter token
        oauth_manager = OAuthTokenManager()
        token = await oauth_manager.get_token()
        
        # Construir URL
        models_url = f"{Config.ONPREMISE_API_BASE_URL}/models"
        print(f"📡 URL: {models_url}")
        print()
        
        # Fazer requisição
        async with httpx.AsyncClient(verify=Config.VERIFY_SSL, timeout=30.0) as client:
            response = await client.get(
                models_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                models = response.json()
                print("✅ API respondeu com sucesso!")
                print()
                print("📦 Modelos disponíveis:")
                print()
                
                if isinstance(models, dict) and "models" in models:
                    model_list = models["models"]
                elif isinstance(models, list):
                    model_list = models
                else:
                    print(f"   Resposta inesperada: {models}")
                    return False
                
                for i, model in enumerate(model_list, 1):
                    if isinstance(model, str):
                        print(f"   {i:2}. {model}")
                    else:
                        name = model.get("name", "unknown")
                        print(f"   {i:2}. {name}")
                
                print()
                print(f"📊 Total: {len(model_list)} modelos")
                return True
            else:
                print(f"❌ Erro HTTP {response.status_code}")
                print(f"   {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_chat_with_model():
    """Testa uma chamada de chat com um modelo real."""
    print("=" * 70)
    print("🧪 TESTE 4: Chamada de Chat")
    print("=" * 70)
    print()
    
    # Usar um modelo leve e rápido para o teste
    test_model = "llama3.2:3b"
    
    print(f"🤖 Testando modelo: {test_model}")
    print()
    
    try:
        # Obter provider
        provider = LLMFactory.get_provider(test_model)
        
        if not provider:
            print(f"❌ Nenhum provider encontrado para {test_model}")
            return False
        
        print(f"✅ Provider encontrado: {provider.__class__.__name__}")
        print()
        
        # Criar mensagens de teste
        messages = [
            LLMMessage(role="system", content="Você é um assistente útil. Responda em português."),
            LLMMessage(role="user", content="Olá! Diga apenas 'Teste bem-sucedido!' como resposta.")
        ]
        
        print("💬 Enviando mensagem de teste...")
        print()
        
        # Fazer chamada
        response_text = ""
        async for chunk in provider.chat(
            messages=messages,
            model=test_model,
            temperature=0.1,
            num_predict=50
        ):
            response_text += chunk
            print(chunk, end="", flush=True)
        
        print()
        print()
        
        if response_text:
            print("✅ Resposta recebida com sucesso!")
            print(f"   Tamanho: {len(response_text)} caracteres")
            return True
        else:
            print("❌ Resposta vazia")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Executa todos os testes."""
    load_dotenv()
    
    print()
    print("🚀 TESTES DO PROVEDOR ON-PREMISE")
    print("=" * 70)
    print()
    print(f"📍 API Base URL: {Config.ONPREMISE_API_BASE_URL}")
    print(f"📍 Chat Endpoint: {Config.ONPREMISE_CHAT_ENDPOINT}")
    print(f"📍 Token URL: {Config.ONPREMISE_TOKEN_URL}")
    print(f"🔒 SSL Verify: {Config.VERIFY_SSL}")
    print()
    
    results = {}
    
    # Teste 1: Detecção de modelos
    print()
    results["detection"] = await test_model_detection()
    
    # Teste 2: OAuth token
    print()
    results["oauth"] = await test_oauth_token()
    
    # Teste 3: Endpoint /models
    print()
    results["models_api"] = await test_api_models_endpoint()
    
    # Teste 4: Chat
    print()
    results["chat"] = await test_chat_with_model()
    
    # Resumo final
    print()
    print("=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    print()
    
    tests = [
        ("Detecção de Modelos", results["detection"]),
        ("Token OAuth", results["oauth"]),
        ("API /models", results["models_api"]),
        ("Chat com Modelo", results["chat"]),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name:30} {status}")
    
    print()
    print(f"{'='*70}")
    
    if passed == total:
        print(f"✅ TODOS OS TESTES PASSARAM! ({passed}/{total})")
        print()
        print("🎉 O provedor on-premise está funcionando perfeitamente!")
    else:
        print(f"⚠️  ALGUNS TESTES FALHARAM ({passed}/{total})")
        print()
        print("🔍 Verifique os erros acima e a configuração do .env")
    
    print(f"{'='*70}")
    print()


if __name__ == "__main__":
    asyncio.run(main())

