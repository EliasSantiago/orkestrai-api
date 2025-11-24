"""
Default Chat Agent - Available to all users.

This is the default agent used when no agent_id is provided in chat requests.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.resolve()
project_root_str = str(project_root)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

from dotenv import load_dotenv
from google.adk.agents import Agent

# Load environment variables
load_dotenv(project_root / '.env')

# Configure Google API key if available
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
if GOOGLE_API_KEY:
    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

# Default chat agent
root_agent = Agent(
    model='gemini-2.5-flash',
    name='chat_geral',  # Must be a valid identifier (no spaces)
    description='Agente de chat geral disponível para todos os usuários',
    instruction='''Você é um assistente de IA útil e prestativo. Seu objetivo é ajudar os usuários com suas perguntas e tarefas de forma clara, precisa e amigável. 

Você pode ajudar com uma ampla variedade de tópicos, incluindo:
- Programação e desenvolvimento de software
- Escrita e edição de texto
- Análise de dados e informações
- Pesquisa e busca de informações
- Resolução de problemas técnicos
- E muito mais

Sempre seja respeitoso, profissional e forneça respostas úteis e informativas. Use português brasileiro quando apropriado.''',
    tools=[],
)

