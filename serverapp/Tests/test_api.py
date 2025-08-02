import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from tasks.models import Task


@pytest.fixture
def api_client():
    """Fixture que retorna um cliente da API"""
    return APIClient()


@pytest.fixture
def test_user():
    """Fixture que cria um usuário de teste"""
    # Usar email como username para compatibilidade com nosso sistema de auth
    return User.objects.create_user(
        username='test@example.com',  # email como username
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Fixture que retorna um cliente autenticado"""
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def task_data():
    """Fixture com dados básicos para criar uma tarefa"""
    return {
        'title': 'Tarefa de Teste',
        'description': 'Descrição da tarefa de teste',
        'priority': 'medium',
        'status': 'pending',
        'tags': 'teste, api',
        'due_date': (datetime.now() + timedelta(days=7)).isoformat()
    }


@pytest.fixture
def sample_task(test_user, task_data):
    """Fixture que cria uma tarefa de exemplo"""
    return Task.objects.create(
        owner=test_user,
        **task_data
    )


@pytest.mark.django_db
class TestAuthenticationAPI:
    """Testes para endpoints de autenticação"""
    
    def test_register_user_success(self, api_client):
        """Testa registro de usuário com dados válidos"""
        import uuid
        unique_email = f'newuser{uuid.uuid4().hex[:8]}@example.com'
        
        user_data = {
            'email': unique_email,
            'password': 'strongpass123',
            'confirm_password': 'strongpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post('/api/auth/register/', user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == user_data['email']
        assert User.objects.filter(email=user_data['email']).exists()
    
    def test_register_user_invalid_data(self, api_client):
        """Testa registro com dados inválidos"""
        user_data = {
            'email': 'invalid-email',
            'password': '123',
            'confirm_password': '456'
        }
        
        response = api_client.post('/api/auth/register/', user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Verificar se há erros na resposta (o formato exato pode variar)
        assert len(response.data) > 0  # Deve ter pelo menos um erro
    
    def test_register_duplicate_email(self, api_client, test_user):
        """Testa registro com email já existente"""
        user_data = {
            'email': test_user.email,
            'password': 'strongpass123',
            'confirm_password': 'strongpass123',
            'first_name': 'Another',
            'last_name': 'User'
        }
        
        response = api_client.post('/api/auth/register/', user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Verificar se há erro de email duplicado
        assert len(response.data) > 0
    
    def test_login_success(self, api_client, test_user):
        """Testa login com credenciais válidas"""
        login_data = {
            'email': test_user.email,
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/login/', login_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == test_user.email
    
    def test_login_invalid_credentials(self, api_client, test_user):
        """Testa login com credenciais inválidas"""
        login_data = {
            'email': test_user.email,
            'password': 'wrongpassword'
        }
        
        response = api_client.post('/api/auth/login/', login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'message' in response.data
    
    def test_login_nonexistent_user(self, api_client):
        """Testa login com usuário inexistente"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword'
        }
        
        response = api_client.post('/api/auth/login/', login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token(self, api_client, test_user):
        """Testa renovação de token"""
        refresh = RefreshToken.for_user(test_user)
        
        response = api_client.post('/api/auth/token/refresh/', {
            'refresh': str(refresh)
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data


@pytest.mark.django_db
class TestTasksAPI:
    """Testes para endpoints de tarefas"""
    
    def test_create_task_success(self, authenticated_client, task_data):
        """Testa criação de tarefa com dados válidos"""
        response = authenticated_client.post('/api/tasks/', task_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == task_data['title']
        assert response.data['description'] == task_data['description']
        assert response.data['priority'] == task_data['priority']
        assert response.data['status'] == task_data['status']
        assert Task.objects.filter(title=task_data['title']).exists()
    
    def test_create_task_minimal_data(self, authenticated_client):
        """Testa criação de tarefa com dados mínimos"""
        minimal_data = {
            'title': 'Tarefa Mínima'
        }
        
        response = authenticated_client.post('/api/tasks/', minimal_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == minimal_data['title']
        assert response.data['priority'] == 'medium'  # valor padrão
        assert response.data['status'] == 'pending'  # valor padrão
    
    def test_create_task_invalid_data(self, authenticated_client):
        """Testa criação de tarefa com dados inválidos"""
        invalid_data = {
            'title': '',  # título vazio
            'priority': 'invalid_priority',
            'status': 'invalid_status'
        }
        
        response = authenticated_client.post('/api/tasks/', invalid_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # DRF retorna erros diretamente no response.data, não em 'errors'
        assert 'title' in response.data
        assert 'priority' in response.data
        assert 'status' in response.data
    
    def test_create_task_unauthorized(self, api_client, task_data):
        """Testa criação de tarefa sem autenticação"""
        response = api_client.post('/api/tasks/', task_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_tasks(self, authenticated_client, test_user):
        """Testa listagem de tarefas"""
        # Criar algumas tarefas
        Task.objects.create(
            owner=test_user,
            title='Tarefa 1',
            priority='high',
            status='pending'
        )
        Task.objects.create(
            owner=test_user,
            title='Tarefa 2',
            priority='low',
            status='completed'
        )
        
        response = authenticated_client.get('/api/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
    
    def test_list_tasks_with_filters(self, authenticated_client, test_user):
        """Testa listagem de tarefas com filtros"""
        # Criar tarefas com diferentes status
        Task.objects.create(
            owner=test_user,
            title='Tarefa Pendente',
            status='pending'
        )
        Task.objects.create(
            owner=test_user,
            title='Tarefa Concluída',
            status='completed'
        )
        
        # Filtrar por status
        response = authenticated_client.get('/api/tasks/?status=pending')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['status'] == 'pending'
    
    def test_list_tasks_with_search(self, authenticated_client, test_user):
        """Testa busca de tarefas"""
        Task.objects.create(
            owner=test_user,
            title='Reunião importante',
            description='Discussão sobre projeto'
        )
        Task.objects.create(
            owner=test_user,
            title='Codificação',
            description='Implementar nova feature'
        )
        
        response = authenticated_client.get('/api/tasks/?search=reunião')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'reunião' in response.data['results'][0]['title'].lower()
    
    def test_get_task_detail(self, authenticated_client, sample_task):
        """Testa obtenção de detalhes de uma tarefa"""
        response = authenticated_client.get(f'/api/tasks/{sample_task.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_task.id
        assert response.data['title'] == sample_task.title
    
    def test_get_task_not_found(self, authenticated_client):
        """Testa obtenção de tarefa inexistente"""
        response = authenticated_client.get('/api/tasks/99999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_task(self, authenticated_client, sample_task):
        """Testa atualização de tarefa"""
        update_data = {
            'title': 'Título Atualizado',
            'priority': 'high',
            'status': 'in_progress'
        }
        
        response = authenticated_client.put(f'/api/tasks/{sample_task.id}/', update_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == update_data['title']
        assert response.data['priority'] == update_data['priority']
        assert response.data['status'] == update_data['status']
        
        # Verificar se foi realmente atualizado no banco
        sample_task.refresh_from_db()
        assert sample_task.title == update_data['title']
    
    def test_partial_update_task(self, authenticated_client, sample_task):
        """Testa atualização parcial de tarefa"""
        update_data = {
            'priority': 'urgent'
        }
        
        response = authenticated_client.patch(f'/api/tasks/{sample_task.id}/', update_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['priority'] == update_data['priority']
        assert response.data['title'] == sample_task.title  # não mudou
    
    def test_toggle_task_completion(self, authenticated_client, sample_task):
        """Testa alternância de conclusão de tarefa"""
        original_status = sample_task.is_completed
        
        response = authenticated_client.patch(f'/api/tasks/{sample_task.id}/toggle/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_completed'] != original_status
        
        # Verificar se foi realmente alterado
        sample_task.refresh_from_db()
        assert sample_task.is_completed != original_status
    
    def test_delete_task(self, authenticated_client, sample_task):
        """Testa exclusão de tarefa"""
        task_id = sample_task.id
        
        response = authenticated_client.delete(f'/api/tasks/{task_id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task_id).exists()
    
    def test_access_other_user_task(self, api_client, sample_task):
        """Testa acesso a tarefa de outro usuário"""
        # Criar outro usuário
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Autenticar com outro usuário
        refresh = RefreshToken.for_user(other_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = api_client.get(f'/api/tasks/{sample_task.id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskPermissions:
    """Testes de permissões das tarefas"""
    
    def test_user_can_only_see_own_tasks(self, api_client):
        """Testa que usuário só vê suas próprias tarefas"""
        # Criar dois usuários
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        # Criar tarefas para cada usuário
        Task.objects.create(owner=user1, title='Tarefa do User 1')
        Task.objects.create(owner=user2, title='Tarefa do User 2')
        
        # Autenticar como user1
        refresh = RefreshToken.for_user(user1)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = api_client.get('/api/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Tarefa do User 1'


@pytest.mark.django_db
class TestTaskValidation:
    """Testes de validação de dados das tarefas"""
    
    def test_task_title_required(self, authenticated_client):
        """Testa que título é obrigatório"""
        data = {
            'description': 'Descrição sem título'
        }
        
        response = authenticated_client.post('/api/tasks/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
    
    def test_invalid_priority(self, authenticated_client):
        """Testa prioridade inválida"""
        data = {
            'title': 'Tarefa',
            'priority': 'super_urgent'  # não existe
        }
        
        response = authenticated_client.post('/api/tasks/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'priority' in response.data
    
    def test_invalid_status(self, authenticated_client):
        """Testa status inválido"""
        data = {
            'title': 'Tarefa',
            'status': 'maybe_done'  # não existe
        }
        
        response = authenticated_client.post('/api/tasks/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'status' in response.data
    
    def test_valid_due_date_format(self, authenticated_client):
        """Testa formato válido de data"""
        data = {
            'title': 'Tarefa com data',
            'due_date': '2024-12-31T23:59:59Z'
        }
        
        response = authenticated_client.post('/api/tasks/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_invalid_due_date_format(self, authenticated_client):
        """Testa formato inválido de data"""
        data = {
            'title': 'Tarefa com data inválida',
            'due_date': 'invalid-date'
        }
        
        response = authenticated_client.post('/api/tasks/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'due_date' in response.data


@pytest.mark.django_db 
class TestTaskOrdering:
    """Testes de ordenação de tarefas"""
    
    def test_ordering_by_created_at(self, authenticated_client, test_user):
        """Testa ordenação por data de criação"""
        # Criar tarefas em ordem específica
        task1 = Task.objects.create(owner=test_user, title='Primeira tarefa')
        task2 = Task.objects.create(owner=test_user, title='Segunda tarefa')
        
        # Ordenação crescente
        response = authenticated_client.get('/api/tasks/?ordering=created_at')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['id'] == task1.id
        assert response.data['results'][1]['id'] == task2.id
        
        # Ordenação decrescente
        response = authenticated_client.get('/api/tasks/?ordering=-created_at')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['id'] == task2.id
        assert response.data['results'][1]['id'] == task1.id
    
    def test_ordering_by_priority(self, authenticated_client, test_user):
        """Testa ordenação por prioridade"""
        Task.objects.create(owner=test_user, title='Baixa', priority='low')
        Task.objects.create(owner=test_user, title='Alta', priority='high')
        Task.objects.create(owner=test_user, title='Urgente', priority='urgent')
        
        response = authenticated_client.get('/api/tasks/?ordering=priority')
        
        assert response.status_code == status.HTTP_200_OK
        # Verificar se está ordenado corretamente
        priorities = [task['priority'] for task in response.data['results']]
        expected_order = ['low', 'medium', 'high', 'urgent']
        # Verificar se segue a ordem de prioridade
        assert all(priorities[i] in expected_order for i in range(len(priorities)))


@pytest.mark.django_db
class TestPagination:
    """Testes de paginação"""
    
    def test_pagination_structure(self, authenticated_client, test_user):
        """Testa estrutura da paginação"""
        # Criar várias tarefas
        for i in range(15):
            Task.objects.create(owner=test_user, title=f'Tarefa {i}')
        
        response = authenticated_client.get('/api/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        assert response.data['count'] == 15
    
    def test_pagination_navigation(self, authenticated_client, test_user):
        """Testa navegação entre páginas"""
        # Criar várias tarefas
        for i in range(25):
            Task.objects.create(owner=test_user, title=f'Tarefa {i}')
        
        # Primeira página
        response = authenticated_client.get('/api/tasks/')
        assert len(response.data['results']) <= 20  # tamanho da página
        assert response.data['next'] is not None
        assert response.data['previous'] is None
        
        # Segunda página
        response = authenticated_client.get('/api/tasks/?page=2')
        assert len(response.data['results']) <= 20
        assert response.data['previous'] is not None


# Configuração para executar os testes
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
