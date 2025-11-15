#!/usr/bin/env python3
"""
Script para testar o roteamento de modelos entre providers.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.core.llm_factory import LLMFactory

# Load environment
load_dotenv()

# Reset factory to reload providers with new logic
LLMFactory.reset()


def test_model_routing():
    """Test model routing to correct providers."""
    
    print("=" * 70)
    print("🧪 TESTE: Roteamento de Modelos")
    print("=" * 70)
    print()
    
    # Models that should go to OnPremise
    onpremise_models = [
        "qwen3:30b-a3b-instruct-2507-q4_K_M",
        "qwen3-coder:30b",
        "deepseek-r1:14b",
        "deepseek-r1:8b",
        "llama3.1:8b-instruct-fp16",
        "llama3.2:3b",
        "gemma3:27b-it-q4_K_M",
        "gemma3:12b-it-fp16",
        "phi4:14b",
        "gpt-oss:20b",
    ]
    
    # Models that should go to Google Gemini
    gemini_models = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
    ]
    
    # Models that should go to OpenAI
    openai_models = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
    ]
    
    print("✅ Testando modelos ON-PREMISE:\n")
    
    correct_onpremise = 0
    for model in onpremise_models:
        provider = LLMFactory.get_provider(model)
        provider_name = provider.__class__.__name__ if provider else "NENHUM"
        
        if provider_name == "OnPremiseProvider":
            print(f"   ✅ {model:45} → {provider_name}")
            correct_onpremise += 1
        else:
            print(f"   ❌ {model:45} → {provider_name} (ERRO! Deveria ser OnPremiseProvider)")
    
    print()
    print(f"📊 On-Premise: {correct_onpremise}/{len(onpremise_models)} corretos")
    print()
    print("-" * 70)
    print()
    print("✅ Testando modelos GOOGLE GEMINI:\n")
    
    correct_gemini = 0
    for model in gemini_models:
        provider = LLMFactory.get_provider(model)
        provider_name = provider.__class__.__name__ if provider else "NENHUM"
        
        if provider_name == "ADKProvider":
            print(f"   ✅ {model:45} → {provider_name}")
            correct_gemini += 1
        else:
            print(f"   ❌ {model:45} → {provider_name} (ERRO! Deveria ser ADKProvider)")
    
    print()
    print(f"📊 Gemini: {correct_gemini}/{len(gemini_models)} corretos")
    print()
    print("-" * 70)
    print()
    print("✅ Testando modelos OPENAI:\n")
    
    correct_openai = 0
    for model in openai_models:
        provider = LLMFactory.get_provider(model)
        provider_name = provider.__class__.__name__ if provider else "NENHUM"
        
        if provider_name == "OpenAIProvider":
            print(f"   ✅ {model:45} → {provider_name}")
            correct_openai += 1
        else:
            print(f"   ❌ {model:45} → {provider_name} (ERRO! Deveria ser OpenAIProvider)")
    
    print()
    print(f"📊 OpenAI: {correct_openai}/{len(openai_models)} corretos")
    print()
    print("=" * 70)
    
    total_correct = correct_onpremise + correct_gemini + correct_openai
    total_models = len(onpremise_models) + len(gemini_models) + len(openai_models)
    
    if total_correct == total_models:
        print("✅ TODOS OS MODELOS FORAM ROTEADOS CORRETAMENTE!")
        print(f"   {total_correct}/{total_models} modelos corretos")
        return True
    else:
        print(f"⚠️  ALGUNS MODELOS FORAM ROTEADOS INCORRETAMENTE")
        print(f"   {total_correct}/{total_models} modelos corretos")
        return False


if __name__ == "__main__":
    success = test_model_routing()
    sys.exit(0 if success else 1)

