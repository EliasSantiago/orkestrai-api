#!/usr/bin/env python3
"""
Script para migrar nomes de modelos para o formato LiteLLM.

Este script atualiza todos os agentes no banco de dados convertendo
os nomes de modelos do formato antigo (gemini-2.0-flash) para o novo
formato LiteLLM (gemini/gemini-2.0-flash).

Usage:
    python scripts/migrate_models_to_litellm_format.py
    
    # Dry run (não faz mudanças, apenas mostra o que seria feito)
    python scripts/migrate_models_to_litellm_format.py --dry-run
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal
from src.models import AgentDB
from sqlalchemy import text


def convert_model_name(old_model: str) -> str:
    """
    Converte nome de modelo do formato antigo para formato LiteLLM.
    
    Args:
        old_model: Nome do modelo no formato antigo (e.g., "gemini-2.0-flash")
        
    Returns:
        Nome do modelo no formato LiteLLM (e.g., "gemini/gemini-2.0-flash")
    """
    # Se já está no formato correto (contém /), retorna como está
    if "/" in old_model:
        return old_model
    
    # Conversões para Gemini
    if old_model.startswith("gemini-"):
        return f"gemini/{old_model}"
    
    # Conversões para OpenAI
    if old_model.startswith("gpt-"):
        return f"openai/{old_model}"
    
    # Conversões para Ollama (com :)
    if ":" in old_model:
        # llama2:latest -> ollama/llama2
        model_name = old_model.split(":")[0]
        return f"ollama/{model_name}"
    
    # Modelos Ollama comuns (sem :)
    ollama_models = ["llama2", "llama3", "mistral", "mixtral", "codellama", "gemma", "phi", "qwen", "deepseek-coder"]
    for ollama_model in ollama_models:
        if old_model.startswith(ollama_model):
            return f"ollama/{old_model}"
    
    # Claude
    if old_model.startswith("claude-"):
        return f"anthropic/{old_model}"
    
    # Se não conseguir converter, retorna como está
    print(f"⚠️  Aviso: Não foi possível converter modelo '{old_model}' automaticamente")
    return old_model


def migrate_models(dry_run: bool = False):
    """
    Migra modelos de agentes para o formato LiteLLM.
    
    Args:
        dry_run: Se True, apenas mostra o que seria feito sem fazer mudanças
    """
    db = SessionLocal()
    
    try:
        print("="*60)
        print("Migração de Modelos para Formato LiteLLM")
        print("="*60)
        print()
        
        if dry_run:
            print("🔍 MODO DRY RUN - Nenhuma mudança será feita")
            print()
        
        # Buscar todos os agentes
        agents = db.query(AgentDB).all()
        
        if not agents:
            print("ℹ️  Nenhum agente encontrado no banco de dados.")
            return
        
        print(f"📊 Total de agentes: {len(agents)}")
        print()
        
        # Contar agentes que precisam ser migrados
        agents_to_migrate = []
        agents_already_migrated = []
        
        for agent in agents:
            if "/" in agent.model:
                agents_already_migrated.append(agent)
            else:
                agents_to_migrate.append(agent)
        
        print(f"✅ Já no formato correto: {len(agents_already_migrated)}")
        print(f"🔄 Precisam ser migrados: {len(agents_to_migrate)}")
        print()
        
        if not agents_to_migrate:
            print("🎉 Todos os agentes já estão no formato LiteLLM!")
            return
        
        # Mostrar agentes que já estão corretos
        if agents_already_migrated:
            print("✅ Agentes já no formato correto:")
            for agent in agents_already_migrated[:5]:  # Mostrar primeiros 5
                print(f"   • ID {agent.id:3d}: {agent.name:30s} → {agent.model}")
            if len(agents_already_migrated) > 5:
                print(f"   ... e mais {len(agents_already_migrated) - 5} agentes")
            print()
        
        # Mostrar e executar migrações
        print("🔄 Agentes a serem migrados:")
        print()
        
        updates_made = 0
        
        for agent in agents_to_migrate:
            old_model = agent.model
            new_model = convert_model_name(old_model)
            
            status = "→" if new_model != old_model else "⚠️"
            print(f"   {status} ID {agent.id:3d}: {agent.name[:30]:30s}")
            print(f"      Antes:  {old_model}")
            print(f"      Depois: {new_model}")
            
            if not dry_run and new_model != old_model:
                agent.model = new_model
                updates_made += 1
            
            print()
        
        # Commit das mudanças
        if not dry_run:
            db.commit()
            print("="*60)
            print(f"✅ Migração concluída! {updates_made} agentes atualizados.")
            print("="*60)
        else:
            print("="*60)
            print(f"🔍 DRY RUN: {len(agents_to_migrate)} agentes seriam atualizados.")
            print("   Execute sem --dry-run para aplicar as mudanças.")
            print("="*60)
        
        # Mostrar exemplos de uso
        if not dry_run and updates_made > 0:
            print()
            print("📝 Exemplos de uso com novos formatos:")
            print()
            print("   # Chat com agente (formato atualizado)")
            print("   curl -X POST http://localhost:8001/api/agents/chat \\")
            print("     -H 'Authorization: Bearer TOKEN' \\")
            print("     -d '{")
            print('       "agent_id": 5,')
            print('       "message": "Olá!",')
            print('       "model": "openai/gpt-4o-mini"  # ← Formato correto agora!')
            print("     }'")
            print()
            
    except Exception as e:
        db.rollback()
        print(f"❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        db.close()


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migrar modelos de agentes para formato LiteLLM"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas mostra o que seria feito, sem fazer mudanças"
    )
    
    args = parser.parse_args()
    
    try:
        migrate_models(dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n\n⚠️  Migração cancelada pelo usuário.")
        sys.exit(1)


if __name__ == "__main__":
    main()

