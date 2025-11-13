#!/usr/bin/env python3
"""
Script para criar agentes usando provedor on-premise.
"""

import requests
import json
import sys
from typing import List, Optional

# Configuração
API_BASE_URL = "http://localhost:8001"

# IMPORTANTE: Obtenha seu token via:
# curl -X POST http://localhost:8001/api/login -H "Content-Type: application/json" -d '{"email":"seu_email","password":"sua_senha"}'
ACCESS_TOKEN = None  # Será solicitado durante execução


def get_access_token() -> str:
    """Solicita credenciais e obtém access token."""
    print("=" * 70)
    print("  LOGIN")
    print("=" * 70)
    
    email = input("\n📧 Email: ").strip()
    password = input("🔒 Senha: ").strip()
    
    print("\n🔐 Autenticando...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Login bem-sucedido!\n")
            return token
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        sys.exit(1)


def create_agent(
    name: str,
    model: str,
    instruction: str,
    description: str = "",
    tools: Optional[List[str]] = None,
    token: str = None
) -> dict:
    """
    Cria um agente via API.
    
    Args:
        name: Nome do agente
        model: Modelo on-premise (ex: gpt-oss:20b)
        instruction: Instruções do agente
        description: Descrição opcional
        tools: Lista de ferramentas (opcional)
        token: Access token de autenticação
    
    Returns:
        Dados do agente criado ou None
    """
    url = f"{API_BASE_URL}/api/agents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": name,
        "description": description,
        "model": model,
        "instruction": instruction,
        "tools": tools or []
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 201:
            agent = response.json()
            print(f"  ✅ {agent['name']}")
            print(f"     ID: {agent['id']}")
            print(f"     Modelo: {agent['model']}")
            print(f"     Ferramentas: {', '.join(agent['tools']) if agent['tools'] else 'Nenhuma'}")
            print()
            return agent
        else:
            print(f"  ❌ Erro ao criar '{name}': {response.status_code}")
            print(f"     {response.text}")
            print()
            return None
            
    except Exception as e:
        print(f"  ❌ Erro ao criar '{name}': {e}")
        print()
        return None


def list_agents(token: str):
    """Lista todos os agentes do usuário."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/agents",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            agents = response.json()
            if agents:
                print(f"\n📋 Total de agentes: {len(agents)}")
                print("\nAgentes criados:")
                for agent in agents:
                    print(f"  • ID {agent['id']}: {agent['name']} ({agent['model']})")
            else:
                print("\n📋 Nenhum agente encontrado")
        else:
            print(f"❌ Erro ao listar agentes: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao listar: {e}")


def main():
    """Cria vários agentes de exemplo."""
    print("=" * 70)
    print("  CRIAR AGENTES ON-PREMISE")
    print("=" * 70)
    
    # Get access token
    global ACCESS_TOKEN
    ACCESS_TOKEN = get_access_token()
    
    # Ask user which agents to create
    print("=" * 70)
    print("  AGENTES DISPONÍVEIS PARA CRIAÇÃO")
    print("=" * 70)
    print("""
1. Assistente Geral (gpt-oss:20b)
2. Especialista Python (llama-2:7b)
3. Analista de Dados (onpremise-analyst:latest)
4. Tradutor (local-translator:multilang)
5. Pesquisador Web (gpt-oss:20b)
6. Todos os acima
7. Personalizado
    """)
    
    choice = input("Escolha uma opção (1-7): ").strip()
    
    print(f"\n{'=' * 70}")
    print("  CRIANDO AGENTES")
    print("=" * 70)
    print()
    
    if choice in ["1", "6"]:
        create_agent(
            name="Assistente On-Premise Geral",
            model="gpt-oss:20b",
            description="Assistente geral para diversas tarefas",
            instruction="Você é um assistente útil que responde em português do Brasil. Seja claro, objetivo e sempre educado nas suas respostas.",
            tools=["calculator", "time"],
            token=ACCESS_TOKEN
        )
    
    if choice in ["2", "6"]:
        create_agent(
            name="Especialista Python On-Premise",
            model="llama-2:7b",
            description="Especialista em programação Python",
            instruction="Você é um expert em Python. Ajude com código, debugging, boas práticas e arquitetura de software. Explique conceitos de forma clara.",
            tools=[],
            token=ACCESS_TOKEN
        )
    
    if choice in ["3", "6"]:
        create_agent(
            name="Analista de Dados On-Premise",
            model="onpremise-analyst:latest",
            description="Especialista em análise de dados e estatística",
            instruction="Você é um analista de dados experiente. Ajude com análises estatísticas, interpretação de dados e visualizações. Use a calculadora quando necessário.",
            tools=["calculator"],
            token=ACCESS_TOKEN
        )
    
    if choice in ["4", "6"]:
        create_agent(
            name="Tradutor On-Premise",
            model="local-translator:multilang",
            description="Tradutor multilíngue profissional",
            instruction="Você é um tradutor profissional. Traduza textos com precisão mantendo o contexto, tom e nuances culturais.",
            tools=[],
            token=ACCESS_TOKEN
        )
    
    if choice in ["5", "6"]:
        create_agent(
            name="Pesquisador Web On-Premise",
            model="gpt-oss:20b",
            description="Pesquisador com acesso à web via Tavily",
            instruction="Você é um pesquisador especializado. Use a ferramenta de busca web para encontrar informações atualizadas e precisas. Sempre cite suas fontes.",
            tools=["web_search", "time"],
            token=ACCESS_TOKEN
        )
    
    if choice == "7":
        print("🎨 Criar agente personalizado\n")
        custom_name = input("Nome do agente: ").strip()
        custom_model = input("Modelo (ex: gpt-oss:20b): ").strip()
        custom_instruction = input("Instrução: ").strip()
        
        tools_input = input("Ferramentas (separadas por vírgula, ex: calculator,time): ").strip()
        custom_tools = [t.strip() for t in tools_input.split(",")] if tools_input else []
        
        print()
        create_agent(
            name=custom_name,
            model=custom_model,
            description=f"Agente personalizado usando {custom_model}",
            instruction=custom_instruction,
            tools=custom_tools,
            token=ACCESS_TOKEN
        )
    
    # Show created agents
    print("=" * 70)
    print("  RESUMO")
    print("=" * 70)
    list_agents(ACCESS_TOKEN)
    
    print("\n✅ Processo concluído!")
    print("\n💡 Próximos passos:")
    print("  1. Teste os agentes via API ou interface web")
    print("  2. Ajuste instruções se necessário")
    print("  3. Configure parâmetros (temperature, num_predict, etc.)")
    print("\n📚 Documentação: docs/ONPREMISE_CREATE_AGENTS_EXAMPLES.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

