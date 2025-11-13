#!/usr/bin/env python3
"""
Script de teste para o provedor on-premise.

Este script valida a configuração do provedor on-premise e testa:
1. Verificação das variáveis de ambiente
2. Geração de token OAuth
3. Requisição de teste ao modelo
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.config import Config
from src.core.oauth_token_manager import OAuthTokenManager
from src.core.llm_providers.onpremise_provider import OnPremiseProvider
from src.core.llm_provider import LLMMessage


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message: str):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"✗ {message}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"⚠ {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ {message}")


def check_environment():
    """Check if all required environment variables are set."""
    print_section("1. VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE")
    
    required_vars = {
        "ONPREMISE_API_BASE_URL": Config.ONPREMISE_API_BASE_URL,
        "ONPREMISE_CHAT_ENDPOINT": Config.ONPREMISE_CHAT_ENDPOINT,
        "ONPREMISE_TOKEN_URL": Config.ONPREMISE_TOKEN_URL,
        "ONPREMISE_CONSUMER_KEY": Config.ONPREMISE_CONSUMER_KEY,
        "ONPREMISE_CONSUMER_SECRET": Config.ONPREMISE_CONSUMER_SECRET,
    }
    
    optional_vars = {
        "ONPREMISE_OAUTH_GRANT_TYPE": Config.ONPREMISE_OAUTH_GRANT_TYPE,
        "ONPREMISE_USERNAME": Config.ONPREMISE_USERNAME,
        "ONPREMISE_PASSWORD": Config.ONPREMISE_PASSWORD,
        "ONPREMISE_MODELS": Config.ONPREMISE_MODELS,
        "VERIFY_SSL": Config.VERIFY_SSL,
    }
    
    all_valid = True
    
    print("\nVariáveis obrigatórias:")
    for var, value in required_vars.items():
        if value:
            # Mask sensitive values
            if "SECRET" in var or "KEY" in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value[:50] + "..." if len(value) > 50 else value
            print_success(f"{var}: {display_value}")
        else:
            print_error(f"{var}: NÃO CONFIGURADA")
            all_valid = False
    
    print("\nVariáveis opcionais:")
    for var, value in optional_vars.items():
        if value:
            if "PASSWORD" in var or "SECRET" in var:
                display_value = "***"
            else:
                display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print_success(f"{var}: {display_value}")
        else:
            print_info(f"{var}: não configurada (opcional)")
    
    # Check grant type
    print("\nTipo de autenticação OAuth:")
    grant_type = Config.ONPREMISE_OAUTH_GRANT_TYPE
    if grant_type == "client_credentials":
        print_info("Usando client_credentials (apenas consumer key/secret)")
    elif grant_type == "password":
        print_info("Usando password grant (requer username/password)")
        if not Config.ONPREMISE_USERNAME or not Config.ONPREMISE_PASSWORD:
            print_error("Username ou password não configurados para password grant!")
            all_valid = False
    else:
        print_warning(f"Grant type desconhecido: {grant_type}")
    
    # Check SSL verification
    if not Config.VERIFY_SSL:
        print_warning("VERIFY_SSL=false - Verificação SSL desabilitada (INSEGURO!)")
    
    return all_valid


async def test_oauth_token():
    """Test OAuth token generation."""
    print_section("2. TESTE DE GERAÇÃO DE TOKEN OAUTH")
    
    try:
        oauth_manager = OAuthTokenManager()
        print_info("OAuthTokenManager criado com sucesso")
        
        print_info("Gerando token OAuth...")
        token = await oauth_manager.get_token()
        
        if token:
            print_success(f"Token gerado com sucesso: {token[:20]}...{token[-10:]}")
            print_info(f"Tamanho do token: {len(token)} caracteres")
            return True
        else:
            print_error("Token vazio retornado")
            return False
            
    except Exception as e:
        print_error(f"Erro ao gerar token: {e}")
        return False


async def test_provider():
    """Test the on-premise provider."""
    print_section("3. TESTE DO PROVEDOR ON-PREMISE")
    
    try:
        provider = OnPremiseProvider()
        print_success("OnPremiseProvider criado com sucesso")
        
        # Get supported models
        models = provider.get_supported_models()
        if models:
            print_info(f"Modelos suportados: {', '.join(models)}")
        else:
            print_info("Nenhuma lista de modelos configurada (aceita qualquer modelo)")
        
        return True
        
    except Exception as e:
        print_error(f"Erro ao criar provider: {e}")
        return False


async def test_chat():
    """Test a chat request."""
    print_section("4. TESTE DE REQUISIÇÃO DE CHAT")
    
    try:
        provider = OnPremiseProvider()
        
        # Ask user for model name
        print_info("\nPor favor, informe o nome do modelo a ser testado:")
        print_info("Exemplos: gpt-oss:20b, llama-2:7b, onpremise-model")
        
        # Get model from user or use default
        model = input("Nome do modelo (ou Enter para pular teste): ").strip()
        
        if not model:
            print_warning("Teste de chat ignorado")
            return True
        
        # Create test messages
        messages = [
            LLMMessage(role="system", content="Você é um assistente útil. Responda em português."),
            LLMMessage(role="user", content="Olá! Por favor, responda apenas 'Olá! Estou funcionando!' para confirmar que está operacional.")
        ]
        
        print_info(f"\nTestando modelo: {model}")
        print_info("Enviando requisição...")
        
        # Collect response
        response_text = ""
        chunk_count = 0
        
        async for chunk in provider.chat(
            messages=messages,
            model=model,
            temperature=0.1,
            num_predict=100
        ):
            response_text += chunk
            chunk_count += 1
            print(chunk, end="", flush=True)
        
        print()  # New line after streaming
        
        if response_text:
            print_success(f"\nResposta recebida com sucesso!")
            print_info(f"Total de chunks: {chunk_count}")
            print_info(f"Tamanho da resposta: {len(response_text)} caracteres")
            return True
        else:
            print_error("Resposta vazia recebida")
            return False
            
    except Exception as e:
        print_error(f"\nErro durante teste de chat: {e}")
        import traceback
        print("\nDetalhes do erro:")
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print_section("TESTE DO PROVEDOR ON-PREMISE")
    print_info("Este script testa a configuração do provedor on-premise")
    print_info(f"Projeto: {project_root}")
    
    # Load environment variables
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print_success(f"Arquivo .env carregado: {env_file}")
    else:
        print_warning(f"Arquivo .env não encontrado: {env_file}")
    
    # Run tests
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Environment variables
    if check_environment():
        tests_passed += 1
    else:
        print_error("\nAlgumas variáveis obrigatórias não estão configuradas!")
        print_info("Configure as variáveis no arquivo .env antes de continuar")
        return
    
    # Test 2: OAuth token generation
    if await test_oauth_token():
        tests_passed += 1
    else:
        print_warning("\nFalha ao gerar token OAuth")
        print_info("Verifique as credenciais e a conectividade com o servidor")
    
    # Test 3: Provider initialization
    if await test_provider():
        tests_passed += 1
    else:
        print_error("\nFalha ao inicializar provider")
        return
    
    # Test 4: Chat request (optional)
    if await test_chat():
        tests_passed += 1
    
    # Summary
    print_section("RESUMO DOS TESTES")
    print(f"\nTestes executados: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print_success("\n🎉 Todos os testes passaram!")
        print_info("O provedor on-premise está configurado e funcionando corretamente")
    elif tests_passed >= 3:
        print_warning("\n⚠️  Configuração básica está OK, mas alguns testes falharam")
        print_info("Verifique os erros acima e ajuste a configuração se necessário")
    else:
        print_error("\n❌ Vários testes falharam")
        print_info("Revise a configuração e consulte a documentação:")
        print_info("docs/ONPREMISE_PROVIDER_SETUP.md")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nErro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

