#!/usr/bin/env python3
"""Script to create default chat agent for all users."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.database import SessionLocal, test_connection
from src.models import User, Agent
from src.auth import get_password_hash
from sqlalchemy import text


def create_default_agent():
    """Create system user and default chat agent."""
    print("=" * 60)
    print("Criando agente padrão de chat...")
    print("=" * 60)
    
    # Test connection
    if not test_connection():
        print("✗ Erro: Não foi possível conectar ao banco de dados")
        exit(1)
    
    db = SessionLocal()
    try:
        # Create or get system user
        system_user = db.query(User).filter(User.email == 'system@orkestrai.local').first()
        
        if not system_user:
            print("Criando usuário sistema...")
            # Generate a secure random password hash (won't be used for login)
            system_user = User(
                name='system',
                email='system@orkestrai.local',
                hashed_password=get_password_hash('system_password_not_for_login'),
                is_active=True
            )
            db.add(system_user)
            db.commit()
            db.refresh(system_user)
            print(f"✓ Usuário sistema criado (ID: {system_user.id})")
        else:
            print(f"✓ Usuário sistema já existe (ID: {system_user.id})")
        
        # Check if default agent already exists
        default_agent = db.query(Agent).filter(
            Agent.name == 'Chat Geral',
            Agent.user_id == system_user.id
        ).first()
        
        if default_agent:
            print(f"✓ Agente padrão já existe (ID: {default_agent.id})")
            print(f"  Nome: {default_agent.name}")
            print(f"  Modelo: {default_agent.model}")
            return default_agent.id
        
        # Create default agent
        print("Criando agente padrão...")
        default_agent = Agent(
            name='Chat Geral',
            description='Agente de chat geral disponível para todos os usuários',
            instruction='Você é um assistente de IA útil e prestativo. Seu objetivo é ajudar os usuários com suas perguntas e tarefas de forma clara, precisa e amigável. Você pode ajudar com uma ampla variedade de tópicos, incluindo programação, escrita, análise, pesquisa e muito mais. Sempre seja respeitoso, profissional e forneça respostas úteis e informativas.',
            model='gpt-4o-mini',
            tools=[],
            use_file_search=False,
            user_id=system_user.id,
            is_active=True
        )
        db.add(default_agent)
        db.commit()
        db.refresh(default_agent)
        
        print(f"✓ Agente padrão criado com sucesso!")
        print(f"  ID: {default_agent.id}")
        print(f"  Nome: {default_agent.name}")
        print(f"  Modelo: {default_agent.model}")
        print(f"  Descrição: {default_agent.description}")
        
        return default_agent.id
        
    except Exception as e:
        print(f"✗ Erro ao criar agente padrão: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    agent_id = create_default_agent()
    print("\n" + "=" * 60)
    print("Agente padrão configurado com sucesso!")
    print(f"ID do agente padrão: {agent_id}")
    print("=" * 60)

