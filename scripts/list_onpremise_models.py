#!/usr/bin/env python3
"""
Script para listar modelos disponíveis na API on-premise.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.core.oauth_token_manager import OAuthTokenManager
import httpx
from src.config import Config


async def list_models():
    """List available models from on-premise API."""
    print("=" * 70)
    print("  MODELOS DISPONÍVEIS NA API ON-PREMISE")
    print("=" * 70)
    
    try:
        # Get OAuth token
        print("\n🔐 Gerando token OAuth...")
        oauth_manager = OAuthTokenManager()
        token = await oauth_manager.get_token()
        print("✓ Token gerado com sucesso")
        
        # Build models endpoint URL
        # Try /models endpoint (GET)
        models_url = f"{Config.ONPREMISE_API_BASE_URL.rstrip('/')}/models"
        
        print(f"\n🌐 Consultando: {models_url}")
        
        # Make request
        async with httpx.AsyncClient(verify=Config.VERIFY_SSL, timeout=30.0) as client:
            response = await client.get(
                models_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"📡 Resposta: HTTP {response.status_code}")
            
            if response.status_code == 200:
                models = response.json()
                print("\n📦 Modelos disponíveis:\n")
                
                # Handle different response formats
                if isinstance(models, dict) and "models" in models:
                    # Format: {"models": [{"name": "...", ...}]}
                    for i, model in enumerate(models["models"], 1):
                        name = model.get("name", "unknown")
                        size = model.get("size", "unknown")
                        modified = model.get("modified_at", "unknown")
                        print(f"  {i}. {name}")
                        print(f"     Size: {size}")
                        if modified != "unknown":
                            print(f"     Modified: {modified}")
                        print()
                
                elif isinstance(models, list):
                    # Format: [{"name": "...", ...}]
                    for i, model in enumerate(models, 1):
                        if isinstance(model, dict):
                            name = model.get("name", "unknown")
                            size = model.get("size", "unknown")
                            print(f"  {i}. {name} (size: {size})")
                        elif isinstance(model, str):
                            print(f"  {i}. {model}")
                        print()
                
                else:
                    # Unknown format, just print
                    print(f"  Resposta: {models}")
                
                # Show usage examples
                print("\n" + "=" * 70)
                print("  COMO USAR ESTES MODELOS")
                print("=" * 70)
                print("\nPara criar um agente com estes modelos, use:")
                print("\n  curl -X POST http://localhost:8001/api/agents \\")
                print("    -H 'Authorization: Bearer SEU_TOKEN' \\")
                print("    -H 'Content-Type: application/json' \\")
                print("    -d '{")
                print('      "name": "Meu Agente",')
                print('      "model": "NOME_DO_MODELO_AQUI",')
                print('      "instruction": "Suas instruções..."')
                print("    }'\n")
                
            else:
                print(f"\n❌ Erro ao consultar modelos:")
                print(f"   Status: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
                # Try to get more details
                if response.status_code == 404:
                    print("\n💡 Dica: O endpoint /models pode não estar disponível.")
                    print("   Consulte a documentação da API para saber quais modelos estão disponíveis.")
                elif response.status_code == 401:
                    print("\n💡 Dica: Erro de autenticação. Verifique as credenciais OAuth no .env")
                
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print("\nDetalhes:")
        traceback.print_exc()
        
        print("\n💡 Dicas:")
        print("  1. Verifique se ONPREMISE_API_BASE_URL está correto no .env")
        print("  2. Verifique se as credenciais OAuth estão corretas")
        print("  3. Verifique conectividade com o servidor")


def main():
    """Main function."""
    # Load environment
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    # Run async function
    asyncio.run(list_models())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário")
        sys.exit(0)

