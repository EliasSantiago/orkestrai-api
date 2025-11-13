#!/usr/bin/env python3
"""
Script para testar a integração do LiteLLM.

Este script verifica:
1. Se o LiteLLM está instalado
2. Se as configurações estão corretas
3. Se os providers estão funcionando
4. Se é possível fazer requisições

Usage:
    python scripts/test_litellm_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.core.llm_factory import LLMFactory
from src.core.llm_provider import LLMMessage


def print_section(title: str):
    """Imprime uma seção formatada."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_installation():
    """Testa se o LiteLLM está instalado."""
    print_section("1. Verificando Instalação")
    
    try:
        import litellm
        print(f"✅ LiteLLM instalado: v{litellm.__version__}")
        return True
    except ImportError:
        print("❌ LiteLLM não está instalado!")
        print("   Execute: pip install litellm>=1.50.0")
        return False


def test_configuration():
    """Testa as configurações."""
    print_section("2. Verificando Configuração")
    
    print(f"LiteLLM Enabled: {'✅' if Config.LITELLM_ENABLED else '❌'} {Config.LITELLM_ENABLED}")
    print(f"LiteLLM Verbose: {Config.LITELLM_VERBOSE}")
    print(f"Num Retries: {Config.LITELLM_NUM_RETRIES}")
    print(f"Request Timeout: {Config.LITELLM_REQUEST_TIMEOUT}s")
    
    print("\nAPI Keys:")
    print(f"  Google API: {'✅ Configurada' if Config.GOOGLE_API_KEY else '❌ Não configurada'}")
    print(f"  OpenAI API: {'✅ Configurada' if Config.OPENAI_API_KEY else '❌ Não configurada'}")
    print(f"  Anthropic API: {'✅ Configurada' if Config.LITELLM_ANTHROPIC_API_KEY else '⚠ Não configurada (opcional)'}")
    print(f"  Ollama Base URL: {Config.OLLAMA_API_BASE_URL or '⚠ Não configurado (opcional)'}")
    
    # Verificar se pelo menos uma API key está configurada
    has_api_key = (
        Config.GOOGLE_API_KEY or 
        Config.OPENAI_API_KEY or 
        Config.LITELLM_ANTHROPIC_API_KEY or
        Config.OLLAMA_API_BASE_URL
    )
    
    if not has_api_key:
        print("\n❌ Nenhuma API key configurada!")
        print("   Configure pelo menos uma no arquivo .env")
        return False
    
    if not Config.LITELLM_ENABLED:
        print("\n⚠ LiteLLM não está habilitado!")
        print("   Configure LITELLM_ENABLED=true no .env")
        return False
    
    return True


def test_providers():
    """Testa os providers disponíveis."""
    print_section("3. Verificando Providers")
    
    try:
        providers = LLMFactory._get_providers()
        print(f"✅ {len(providers)} providers encontrados:\n")
        
        litellm_found = False
        
        for provider in providers:
            provider_name = provider.__class__.__name__
            models = provider.get_supported_models()
            
            if provider_name == "LiteLLMProvider":
                litellm_found = True
                print(f"  ✅ {provider_name} ({len(models)} modelos)")
            else:
                print(f"  • {provider_name} ({len(models)} modelos)")
            
            # Mostrar primeiros 3 modelos
            for model in models[:3]:
                print(f"      - {model}")
            if len(models) > 3:
                print(f"      ... e mais {len(models) - 3} modelos")
        
        if not litellm_found:
            print("\n⚠ LiteLLMProvider não foi encontrado!")
            print("   Possíveis causas:")
            print("   - LITELLM_ENABLED=false no .env")
            print("   - Erro na inicialização do provider")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar providers: {e}")
        return False


async def test_chat_request():
    """Testa uma requisição de chat."""
    print_section("4. Testando Requisição de Chat")
    
    # Determinar qual modelo usar baseado nas API keys disponíveis
    test_model = None
    
    if Config.GOOGLE_API_KEY:
        test_model = "gemini/gemini-2.0-flash-exp"
    elif Config.OPENAI_API_KEY:
        test_model = "openai/gpt-4o-mini"
    elif Config.LITELLM_ANTHROPIC_API_KEY:
        test_model = "anthropic/claude-3-haiku-20240307"
    elif Config.OLLAMA_API_BASE_URL:
        test_model = "ollama/llama2"
    
    if not test_model:
        print("❌ Nenhum modelo disponível para teste")
        return False
    
    print(f"Usando modelo: {test_model}")
    
    try:
        # Obter provider
        provider = LLMFactory.get_provider(test_model)
        
        if not provider:
            print(f"❌ Provider não encontrado para modelo: {test_model}")
            return False
        
        print(f"Provider: {provider.__class__.__name__}")
        
        # Criar mensagem de teste
        messages = [
            LLMMessage(role="user", content="Diga 'olá' em uma palavra.")
        ]
        
        print("\nResposta: ", end="", flush=True)
        
        # Fazer requisição
        response_received = False
        async for chunk in provider.chat(
            messages=messages,
            model=test_model,
            max_tokens=10
        ):
            print(chunk, end="", flush=True)
            response_received = True
        
        print("\n")
        
        if response_received:
            print("✅ Teste de chat bem-sucedido!")
            return True
        else:
            print("❌ Nenhuma resposta recebida")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro no teste de chat: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_support():
    """Testa suporte a diferentes modelos."""
    print_section("5. Verificando Suporte a Modelos")
    
    test_models = [
        "gemini/gemini-2.0-flash-exp",
        "openai/gpt-4o",
        "anthropic/claude-3-opus-20240229",
        "ollama/llama2",
    ]
    
    for model in test_models:
        supported = LLMFactory.is_model_supported(model)
        status = "✅" if supported else "❌"
        print(f"  {status} {model}")
    
    return True


async def main():
    """Função principal."""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║         Teste de Integração LiteLLM                      ║
    ║         ADK Google API                                   ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Instalação", test_installation),
        ("Configuração", test_configuration),
        ("Providers", test_providers),
        ("Suporte a Modelos", test_model_support),
    ]
    
    results = []
    
    # Executar testes síncronos
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Erro no teste '{test_name}': {e}")
            results.append((test_name, False))
    
    # Executar teste de chat (assíncrono)
    try:
        chat_result = await test_chat_request()
        results.append(("Requisição de Chat", chat_result))
    except Exception as e:
        print(f"\n❌ Erro no teste de chat: {e}")
        results.append(("Requisição de Chat", False))
    
    # Resumo
    print_section("Resumo dos Testes")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passou, {failed} falhou")
    
    if failed == 0:
        print("\n🎉 Todos os testes passaram! LiteLLM está pronto para uso.")
        print("\nPróximos passos:")
        print("  1. Leia a documentação: docs/arquitetura/litellm/README.md")
        print("  2. Veja exemplos de uso: docs/arquitetura/litellm/USAGE.md")
        print("  3. Crie seus agentes usando LiteLLM!")
        return 0
    else:
        print("\n⚠ Alguns testes falharam. Verifique a configuração.")
        print("\nPara resolver:")
        print("  1. Consulte: docs/arquitetura/litellm/TROUBLESHOOTING.md")
        print("  2. Verifique o arquivo .env")
        print("  3. Execute com verbose: LITELLM_VERBOSE=true")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

