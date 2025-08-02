#!/usr/bin/env python3
import requests
import random
from datetime import datetime, timedelta
import getpass

# Configurações da API
API_BASE_URL = "http://localhost:8000"

# Headers base
BASE_HEADERS = {
    "Content-Type": "application/json",
}

# Dados para gerar tarefas aleatórias
TASK_TITLES = [
    "Revisar relatório mensal",
    "Reunião com equipe de desenvolvimento", 
    "Atualizar documentação do projeto",
    "Fazer backup dos arquivos importantes",
    "Responder e-mails pendentes",
    "Preparar apresentação para cliente",
    "Testar nova funcionalidade",
    "Organizar arquivos do computador",
    "Estudar nova tecnologia",
    "Planejar próximo sprint",
    "Corrigir bugs reportados",
    "Implementar autenticação JWT",
    "Configurar ambiente de produção",
    "Criar testes unitários",
    "Refatorar código legado",
    "Analisar métricas de performance",
    "Fazer code review",
    "Atualizar dependências do projeto",
    "Documentar API endpoints",
    "Configurar monitoramento",
    "Implementar sistema de logs",
    "Otimizar consultas ao banco",
    "Criar dashboard administrativo",
    "Integrar com serviço externo",
    "Implementar cache Redis",
    "Configurar CI/CD pipeline",
    "Fazer deploy em produção",
    "Treinar novo membro da equipe",
    "Participar de daily standup",
    "Revisar proposta comercial",
    "Atualizar perfil profissional",
    "Organizar desktop",
    "Fazer backup do banco de dados",
    "Configurar SSL certificado",
    "Implementar websockets",
    "Criar sistema de notificações",
    "Otimizar frontend",
    "Configurar Docker containers",
    "Fazer análise de segurança",
    "Implementar dark mode",
    "Criar sistema de busca",
    "Configurar load balancer",
    "Implementar internacionalização",
    "Fazer testes de usabilidade",
    "Atualizar README do projeto",
    "Configurar ambiente de desenvolvimento",
    "Implementar sistema de comentários",
    "Fazer migração de dados",
    "Configurar backup automático",
    "Criar API documentation"
]

DESCRIPTIONS = [
    "Tarefa importante que precisa ser concluída com atenção aos detalhes.",
    "Atividade de rotina que faz parte do fluxo de trabalho diário.",
    "Projeto estratégico com impacto direto nos resultados da empresa.",
    "Manutenção preventiva para garantir o bom funcionamento do sistema.",
    "Atividade de aprendizado para desenvolvimento profissional.",
    "Tarefa colaborativa que envolve múltiplos membros da equipe.",
    "Otimização de processo para melhorar a eficiência operacional.",
    "Implementação de nova funcionalidade solicitada pelo cliente.",
    "Correção de problema reportado pelos usuários finais.",
    "Atualização de segurança crítica para proteger os dados.",
    "Documentação técnica para facilitar futuras manutenções.",
    "Análise de dados para suporte à tomada de decisões.",
    "Configuração de ambiente para melhorar o workflow.",
    "Teste de qualidade para garantir a estabilidade do sistema.",
    "Reunião de alinhamento para definir próximos passos.",
    "",  # Algumas tarefas sem descrição
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
    "",  # Algumas sem tags
    "",
]

def login():
    """Faz login e retorna o token de acesso"""
    print("🔐 Fazendo login...")
    
    # Credenciais padrão (você pode alterar se necessário)
    email = input("Digite seu email: ")
    password = getpass.getpass("Digite sua senha: ")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login/",
            headers=BASE_HEADERS,
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login realizado com sucesso!")
            return f"Bearer {token}"
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão no login: {e}")
        return None

def generate_random_date():
    """Gera uma data aleatória entre 30 dias atrás e 30 dias no futuro"""
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now() + timedelta(days=30)
    
    random_days = random.randint(0, (end_date - start_date).days)
    random_date = start_date + timedelta(days=random_days)
    
    # Adiciona horário aleatório
    random_hour = random.randint(8, 18)  # Entre 8h e 18h
    random_minute = random.choice([0, 15, 30, 45])  # Minutos "redondos"
    
    return random_date.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)

def create_random_task():
    """Cria dados de uma tarefa aleatória"""
    title = random.choice(TASK_TITLES)
    description = random.choice(DESCRIPTIONS)
    priority = random.choice(PRIORITIES)
    status = random.choice(STATUSES)
    tags = random.choice(TAGS_LIST)
    
    # 70% das tarefas terão data de vencimento
    due_date = None
    if random.random() < 0.7:
        due_date = generate_random_date().isoformat()
    
    task_data = {
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "tags": tags,
    }
    
    if due_date:
        task_data["due_date"] = due_date
    
    return task_data

def create_task(task_data, headers):
    """Cria uma tarefa via API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/tasks/",
            headers=headers,
            json=task_data
        )
        
        if response.status_code == 201:
            task = response.json()
            print(f"✅ Tarefa criada: {task['title']} (ID: {task['id']})")
            return task
        else:
            print(f"❌ Erro ao criar tarefa: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def toggle_task_completion(task_id, headers):
    """Alterna o status de conclusão de uma tarefa"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/api/tasks/{task_id}/toggle/",
            headers=headers
        )
        
        if response.status_code == 200:
            task = response.json()
            status = "concluída" if task.get('is_completed') else "pendente"
            print(f"🔄 Tarefa {task_id} marcada como {status}")
            return task
        else:
            print(f"❌ Erro ao atualizar tarefa {task_id}: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão ao atualizar tarefa {task_id}: {e}")
        return None

def main():
    """Função principal que cria 50 tarefas aleatórias"""
    print("🚀 Iniciando criação de tarefas aleatórias...")
    print("-" * 80)
    
    # Fazer login primeiro
    token = login()
    if not token:
        print("❌ Não foi possível fazer login. Encerrando script.")
        return
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    
    print(f"📊 Criando 50 tarefas...")
    print("-" * 80)
    
    created_tasks = []
    
    # Criar 50 tarefas
    for i in range(50):
        print(f"📝 Criando tarefa {i+1}/50...")
        
        task_data = create_random_task()
        task = create_task(task_data, headers)
        
        if task:
            created_tasks.append(task)
            
            # 50% de chance de marcar como concluída (para tarefas com status 'completed')
            if task_data['status'] == 'completed' and random.random() < 0.8:
                toggle_task_completion(task['id'], headers)
        
        # Pequena pausa para não sobrecarregar a API
        import time
        time.sleep(0.1)
    
    print("-" * 80)
    print(f"✅ Processo concluído! {len(created_tasks)} tarefas criadas com sucesso.")
    
    # Estatísticas
    if created_tasks:
        priorities = [task.get('priority', 'unknown') for task in created_tasks]
        statuses = [task.get('status', 'unknown') for task in created_tasks]
        
        print("\n📊 Estatísticas das tarefas criadas:")
        print(f"   - Prioridades: {dict([(p, priorities.count(p)) for p in set(priorities)])}")
        print(f"   - Status: {dict([(s, statuses.count(s)) for s in set(statuses)])}")
        print(f"   - Total de tarefas: {len(created_tasks)}")

if __name__ == "__main__":
    main()
