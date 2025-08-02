#!/usr/bin/env python3
"""
Script para verificar tarefas no Cosmos DB
Execute: python check_cosmos_tasks.py
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todolist_project.settings')
django.setup()

from core.cosmos_service import CosmosService

def check_tasks_count():
    """Verifica a quantidade de tarefas no Cosmos DB"""
    try:
        cosmos_service = CosmosService()
        
        # Query para contar todas as tarefas
        count_query = "SELECT VALUE COUNT(1) FROM c"
        
        print("🔍 Verificando tarefas no Cosmos DB...")
        print("=" * 50)
        
        # Executar query de contagem
        try:
            items = list(cosmos_service.container.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))
            total_tasks = items[0] if items else 0
            print(f"📊 Total de tarefas: {total_tasks}")
        except Exception as e:
            print(f"❌ Erro ao contar tarefas: {e}")
            return
        
        if total_tasks > 0:
            # Query para detalhes das tarefas
            details_query = """
                SELECT 
                    c.id,
                    c.title,
                    c.status,
                    c.priority,
                    c.is_completed,
                    c.created_at,
                    c.due_date,
                    c.user_id
                FROM c
                ORDER BY c.created_at DESC
            """
            
            print("\n📋 Detalhes das tarefas:")
            print("-" * 80)
            
            try:
                tasks = list(cosmos_service.container.query_items(
                    query=details_query,
                    enable_cross_partition_query=True
                ))
                
                for i, task in enumerate(tasks, 1):
                    status_emoji = "✅" if task.get('is_completed') else "⏳"
                    priority_emoji = {
                        'low': '🟢',
                        'medium': '🟡', 
                        'high': '🟠',
                        'urgent': '🔴'
                    }.get(task.get('priority', 'medium'), '⚪')
                    
                    print(f"{i:2d}. {status_emoji} {priority_emoji} {task.get('title', 'Sem título')}")
                    print(f"    Status: {task.get('status', 'N/A')} | Prioridade: {task.get('priority', 'N/A')}")
                    print(f"    Criado: {task.get('created_at', 'N/A')}")
                    print(f"    Usuário ID: {task.get('user_id', 'N/A')}")
                    print(f"    ID: {task.get('id', 'N/A')}")
                    print()
                    
            except Exception as e:
                print(f"❌ Erro ao buscar detalhes das tarefas: {e}")
            
            # Query para contar por status
            status_query = """
                SELECT 
                    c.status,
                    COUNT(1) as count
                FROM c
                GROUP BY c.status
            """
            
            print("\n📈 Tarefas por status:")
            print("-" * 30)
            
            try:
                status_counts = list(cosmos_service.container.query_items(
                    query=status_query,
                    enable_cross_partition_query=True
                ))
                
                for status_info in status_counts:
                    status = status_info.get('status', 'N/A')
                    count = status_info.get('count', 0)
                    print(f"  {status}: {count}")
                    
            except Exception as e:
                print(f"❌ Erro ao contar por status: {e}")
                
            # Query para contar concluídas vs pendentes
            completion_query = """
                SELECT 
                    SUM(c.is_completed ? 1 : 0) as completed_tasks,
                    SUM(c.is_completed ? 0 : 1) as pending_tasks
                FROM c
            """
            
            print("\n🎯 Status de conclusão:")
            print("-" * 25)
            
            try:
                completion_stats = list(cosmos_service.container.query_items(
                    query=completion_query,
                    enable_cross_partition_query=True
                ))
                
                if completion_stats:
                    stats = completion_stats[0]
                    completed = stats.get('completed_tasks', 0)
                    pending = stats.get('pending_tasks', 0)
                    print(f"  ✅ Concluídas: {completed}")
                    print(f"  ⏳ Pendentes: {pending}")
                    
            except Exception as e:
                print(f"❌ Erro ao contar por conclusão: {e}")
        
        else:
            print("📝 Nenhuma tarefa encontrada no Cosmos DB")
            
    except Exception as e:
        print(f"❌ Erro ao conectar com Cosmos DB: {e}")

if __name__ == '__main__':
    check_tasks_count()
