#!/usr/bin/env python3
import os
import sys
import django
import random
from datetime import timedelta

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todolist_project.settings')
    django.setup()

from django.contrib.auth.models import User
from tasks.models import Task
from django.utils import timezone

TASK_TITLES = [
    "Revisar relatório mensal em equipe",
    "Reunião com equipe de desenvolvimento", 
    "Atualizar documentação do projeto colaborativo",
    "Fazer backup dos arquivos importantes compartilhados",
    "Responder e-mails pendentes da equipe",
    "Preparar apresentação para cliente em conjunto",
    "Testar nova funcionalidade colaborativamente",
    "Organizar arquivos do computador da equipe",
    "Estudar nova tecnologia em grupo",
    "Planejar próximo sprint colaborativo",
    "Corrigir bugs reportados - trabalho em equipe",
    "Implementar autenticação JWT - projeto conjunto",
    "Configurar ambiente de produção colaborativo",
    "Criar testes unitários em dupla",
    "Refatorar código legado - esforço conjunto",
    "Analisar métricas de performance da equipe",
    "Fazer code review colaborativo",
    "Atualizar dependências do projeto compartilhado",
    "Documentar API endpoints - trabalho conjunto",
    "Configurar monitoramento da equipe",
    "Implementar sistema de logs colaborativo",
    "Otimizar consultas ao banco - projeto conjunto",
    "Criar dashboard administrativo colaborativo",
    "Integrar com serviço externo - equipe",
    "Implementar cache Redis - projeto conjunto",
    "Configurar CI/CD pipeline colaborativo",
    "Fazer deploy em produção - equipe DevOps",
    "Treinar novo membro da equipe",
    "Participar de daily standup",
    "Revisar proposta comercial em conjunto",
    "Atualizar perfil profissional da equipe",
    "Organizar desktop compartilhado",
    "Fazer backup do banco de dados - tarefa crítica",
    "Configurar SSL certificado - segurança da equipe",
    "Implementar websockets colaborativos",
    "Criar sistema de notificações da equipe",
    "Otimizar frontend - trabalho conjunto",
    "Configurar Docker containers colaborativos",
    "Fazer análise de segurança da equipe",
    "Implementar dark mode - projeto UX",
    "Criar sistema de busca colaborativo",
    "Configurar load balancer - infraestrutura",
    "Implementar internacionalização conjunta",
    "Fazer testes de usabilidade em equipe",
    "Atualizar README do projeto colaborativo",
    "Configurar ambiente de desenvolvimento conjunto",
    "Implementar sistema de comentários da equipe",
    "Fazer migração de dados - operação crítica",
    "Configurar backup automático da equipe",
    "Criar API documentation colaborativa",
    "Revisão de código em pares",
    "Workshop de tecnologia para equipe",
    "Planejamento estratégico trimestral",
    "Implementação de feature em equipe",
    "Debugging colaborativo de sistema crítico"
]

DESCRIPTIONS = [
    "Tarefa importante que precisa ser concluída com atenção aos detalhes. Colaboração entre equipes necessária.",
    "Atividade de rotina que faz parte do fluxo de trabalho diário da equipe.",
    "Projeto estratégico com impacto direto nos resultados da empresa. Requires multiple team members.",
    "Manutenção preventiva para garantir o bom funcionamento do sistema compartilhado.",
    "Atividade de aprendizado para desenvolvimento profissional da equipe.",
    "Tarefa colaborativa que envolve múltiplos membros da equipe trabalhando em conjunto.",
    "Otimização de processo para melhorar a eficiência operacional da equipe.",
    "Implementação de nova funcionalidade solicitada pelo cliente - trabalho em equipe.",
    "Correção de problema reportado pelos usuários finais - suporte colaborativo.",
    "Atualização de segurança crítica para proteger os dados da organização.",
    "Documentação técnica para facilitar futuras manutenções pela equipe.",
    "Análise de dados para suporte à tomada de decisões estratégicas em grupo.",
    "Configuração de ambiente para melhorar o workflow da equipe de desenvolvimento.",
    "Teste de qualidade para garantir a estabilidade do sistema - QA colaborativo.",
    "Reunião de alinhamento para definir próximos passos do projeto em equipe.",
    "Task requires close collaboration between frontend and backend teams.",
    "Cross-functional project involving multiple departments and stakeholders.",
    "Critical infrastructure work that impacts the entire development team.",
    "",  
    "",
    ""
]

PRIORITIES = ["low", "medium", "high", "urgent"]
STATUSES = ["pending", "in_progress", "completed", "cancelled"]

TAGS_LIST = [
    "Urgente, Reunião",
    "Desenvolvimento, Backend",
    "Frontend, React",
    "DevOps, Infraestrutura", 
    "Documentação",
    "Teste, QA",
    "Segurança, SSL",
    "Performance, Otimização",
    "Database, SQL",
    "API, REST",
    "Mobile, App",
    "Design, UI/UX",
    "Backup, Manutenção",
    "Treinamento, Capacitação",
    "Cliente, Comercial",
    "Bug, Correção",
    "Feature, Nova funcionalidade",
    "Refatoração, Limpeza",
    "Monitoramento, Logs",
    "Deploy, Produção",
    "",  
    "",
]

def get_available_users():
    return User.objects.all()

def generate_random_date():
    start_date = timezone.now() - timedelta(days=30)
    end_date = timezone.now() + timedelta(days=30)
    random_days = random.randint(0, (end_date - start_date).days)
    random_date = start_date + timedelta(days=random_days)
    random_hour = random.randint(8, 18)
    random_minute = random.choice([0, 15, 30, 45])
    return random_date.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)

def create_random_task_data():
    title = random.choice(TASK_TITLES)
    description = random.choice(DESCRIPTIONS)
    priority = random.choice(PRIORITIES)
    status = random.choice(STATUSES)
    tags = random.choice(TAGS_LIST)
    due_date = None
    if random.random() < 0.7:
        due_date = generate_random_date()
    task_data = {
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "tags": tags,
        "due_date": due_date,
    }
    return task_data

def create_task_in_db(task_data, owner_user):
    try:
        task = Task.objects.create(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            status=task_data["status"],
            tags=task_data["tags"],
            due_date=task_data["due_date"],
            owner=owner_user
        )
        if task_data["status"] == "completed":
            task.is_completed = True
            task.completed_at = timezone.now()
            task.save()
        print(f"✅ Tarefa criada: {task.title} (ID: {task.id}) - Owner: {owner_user.username}")
        return task
    except Exception as e:
        print(f"❌ Erro ao criar tarefa: {e}")
        return None

def share_task_with_users(task, users_to_share):
    shared_count = 0
    for user in users_to_share:
        if user != task.owner:
            try:
                task.share_with_user(user)
                shared_count += 1
                print(f"     ✅ Compartilhada com {user.username} ({user.email})")
            except Exception as e:
                print(f"     ❌ Falha ao compartilhar com {user.username}: {e}")
    return shared_count

def get_random_users_to_share(available_users, max_users=2):
    if len(available_users) <= 1:
        return []
    num_users = random.randint(1, min(max_users, len(available_users) - 1))
    return random.sample(list(available_users), num_users)

def create_shared_task(owner_user, available_users, force_share=False):
    task_data = create_random_task_data()
    task = create_task_in_db(task_data, owner_user)
    if not task:
        return None
    shared_count = 0
    if force_share or random.random() < 0.6:
        users_to_share = get_random_users_to_share(available_users)
        if users_to_share:
            print(f"  📤 Compartilhando tarefa '{task.title[:40]}...' com {len(users_to_share)} usuário(s)...")
            shared_count = share_task_with_users(task, users_to_share)
        else:
            print(f"  📝 Tarefa '{task.title[:40]}...' criada sem compartilhamento (poucos usuários)")
    else:
        print(f"  📝 Tarefa '{task.title[:40]}...' criada como pessoal")
    task.shared_count = shared_count
    return task

def main():
    print("🚀 Iniciando criação de tarefas no SQLite usando Django ORM...")
    available_users = get_available_users()
    if not available_users.exists():
        print("❌ Nenhum usuário encontrado no sistema! Crie usuários primeiro.")
        return
    print(f"👥 Usuários encontrados no sistema ({available_users.count()}):")
    for user in available_users:
        print(f"   - {user.username} ({user.email}) - {user.first_name} {user.last_name}")
    if available_users.count() < 2:
        print("⚠️  Aviso: Menos de 2 usuários no sistema. Compartilhamento será limitado.")
    print("📊 Criando 10 tarefas - 5 compartilhadas e 5 pessoais")
    print("-" * 80)
    created_tasks = []
    total_shares = 0
    shared_tasks_count = 0
    target_shared_tasks = 5
    main_owner = available_users.first()
    print(f"👤 Usuário principal (dono das tarefas): {main_owner.username}")
    print("-" * 80)
    for i in range(10):
        force_share = shared_tasks_count < target_shared_tasks and (i < target_shared_tasks or (10 - i) <= (target_shared_tasks - shared_tasks_count))
        print(f"📝 Criando tarefa {i+1}/10...")
        task = create_shared_task(main_owner, available_users, force_share)
        if task:
            created_tasks.append(task)
            total_shares += getattr(task, 'shared_count', 0)
            if getattr(task, 'shared_count', 0) > 0:
                shared_tasks_count += 1
    print("-" * 80)
    print(f"✅ Processo concluído! {len(created_tasks)} tarefas criadas com sucesso.")
    print(f"🤝 Total de compartilhamentos realizados: {total_shares}")
    print(f"📊 Tarefas compartilhadas: {shared_tasks_count}/10 (meta: 5)")
    if created_tasks:
        priorities = [task.priority for task in created_tasks]
        statuses = [task.status for task in created_tasks]
        shared_tasks = [task for task in created_tasks if getattr(task, 'shared_count', 0) > 0]
        personal_tasks = [task for task in created_tasks if getattr(task, 'shared_count', 0) == 0]
        print("\n📊 Estatísticas das tarefas criadas:")
        print(f"   - Prioridades: {dict([(p, priorities.count(p)) for p in set(priorities)])}")
        print(f"   - Status: {dict([(s, statuses.count(s)) for s in set(statuses)])}")
        print(f"   - Com data de vencimento: {len([t for t in created_tasks if t.due_date])}")
        print(f"   - Tarefas pessoais: {len(personal_tasks)}")
        print(f"   - Tarefas compartilhadas: {len(shared_tasks)}")
        if shared_tasks:
            print("\n🤝 Detalhes do compartilhamento:")
            share_distribution = {}
            for task in shared_tasks:
                count = getattr(task, 'shared_count', 0)
                share_distribution[count] = share_distribution.get(count, 0) + 1
            for count, num_tasks in share_distribution.items():
                print(f"   - {num_tasks} tarefa(s) compartilhada(s) com {count} usuário(s)")
            print("\n📋 Lista de tarefas compartilhadas:")
            for i, task in enumerate(shared_tasks, 1):
                shared_users = task.get_shared_users()
                users_str = ", ".join([f"{u.username} ({u.email})" for u in shared_users])
                print(f"   {i}. '{task.title[:40]}...' → {users_str}")
        if personal_tasks:
            print("\n📝 Lista de tarefas pessoais:")
            for i, task in enumerate(personal_tasks, 1):
                print(f"   {i}. '{task.title[:50]}...'")
        print("\n💡 Resultado: As tarefas compartilhadas agora aparecem no banco SQLite!")
        print("   Verifique no Django shell:")
        print("   >>> from tasks.models import Task")
        print("   >>> Task.objects.filter(shared_with__isnull=False).distinct()")
        print("   >>> # Para ver tarefas compartilhadas de um usuário específico:")
        print("   >>> user = User.objects.get(username='username')")
        print("   >>> user.shared_tasks.all()")

if __name__ == "__main__":
    main()
