import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
from tasks.models import Task

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return User.objects.create_user(
        username='test@example.com',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def second_test_user():
    return User.objects.create_user(
        username='test2@example.com',
        email='test2@example.com',
        password='testpass123',
        first_name='Test2',
        last_name='User2'
    )

@pytest.fixture
def authenticated_client(api_client, test_user):
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def second_authenticated_client(api_client, second_test_user):
    refresh = RefreshToken.for_user(second_test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def task_data():
    return {
        'title': 'Tarefa de Teste',
        'description': 'Descrição da tarefa de teste',
        'priority': 'medium',
        'status': 'pending',
        'tags': 'teste, api',
        'due_date': (timezone.now() + timedelta(days=7)).isoformat()
    }

@pytest.fixture
def sample_task(test_user, task_data):
    return Task.objects.create(
        owner=test_user,
        **task_data
    )

@pytest.fixture
def shared_task(test_user, second_test_user):
    task = Task.objects.create(
        owner=test_user,
        title='Tarefa Compartilhada',
        description='Tarefa compartilhada entre usuários',
        priority='high'
    )
    task.share_with_user(second_test_user)
    return task

@pytest.mark.django_db
class TestAuthenticationAPI:
    def test_register_user_success(self, api_client):
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
        user_data = {
            'email': 'invalid-email',
            'password': '123',
            'confirm_password': '456'
        }
        response = api_client.post('/api/auth/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert len(response.data) > 0

    def test_register_duplicate_email(self, api_client, test_user):
        user_data = {
            'email': test_user.email,
            'password': 'strongpass123',
            'confirm_password': 'strongpass123',
            'first_name': 'Another',
            'last_name': 'User'
        }
        response = api_client.post('/api/auth/register/', user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert len(response.data) > 0

    def test_login_success(self, api_client, test_user):
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
        login_data = {
            'email': test_user.email,
            'password': 'wrongpassword'
        }
        response = api_client.post('/api/auth/login/', login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'message' in response.data

    def test_login_nonexistent_user(self, api_client):
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword'
        }
        response = api_client.post('/api/auth/login/', login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, api_client, test_user):
        refresh = RefreshToken.for_user(test_user)
        response = api_client.post('/api/auth/token/refresh/', {
            'refresh': str(refresh)
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

@pytest.mark.django_db
class TestTasksAPI:
    def test_create_task_success(self, authenticated_client, task_data):
        response = authenticated_client.post('/api/tasks/', task_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == task_data['title']
        assert response.data['description'] == task_data['description']
        assert response.data['priority'] == task_data['priority']
        assert response.data['status'] == task_data['status']
        assert Task.objects.filter(title=task_data['title']).exists()

    def test_create_task_minimal_data(self, authenticated_client):
        minimal_data = {
            'title': 'Tarefa Mínima'
        }
        response = authenticated_client.post('/api/tasks/', minimal_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == minimal_data['title']
        assert response.data['priority'] == 'medium'
        assert response.data['status'] == 'pending'

    def test_create_task_invalid_data(self, authenticated_client):
        invalid_data = {
            'title': '',
            'priority': 'invalid_priority',
            'status': 'invalid_status'
        }
        response = authenticated_client.post('/api/tasks/', invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
        assert 'priority' in response.data
        assert 'status' in response.data

    def test_create_task_unauthorized(self, api_client, task_data):
        response = api_client.post('/api/tasks/', task_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_tasks_includes_owned_and_shared(self, authenticated_client, test_user, second_test_user):
        Task.objects.create(
            owner=test_user,
            title='Minha Tarefa',
            priority='high'
        )
        shared_task = Task.objects.create(
            owner=second_test_user,
            title='Tarefa Compartilhada',
            priority='medium'
        )
        shared_task.share_with_user(test_user)
        Task.objects.create(
            owner=second_test_user,
            title='Tarefa Privada',
            priority='low'
        )
        response = authenticated_client.get('/api/tasks/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        task_titles = [task['title'] for task in response.data['results']]
        assert 'Minha Tarefa' in task_titles
        assert 'Tarefa Compartilhada' in task_titles
        assert 'Tarefa Privada' not in task_titles

    def test_list_tasks_with_filters(self, authenticated_client, test_user):
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
        response = authenticated_client.get('/api/tasks/?status=pending')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['status'] == 'pending'

    def test_list_tasks_with_search(self, authenticated_client, test_user):
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

    def test_get_task_detail_own_task(self, authenticated_client, sample_task):
        response = authenticated_client.get(f'/api/tasks/{sample_task.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_task.id
        assert response.data['title'] == sample_task.title

    def test_get_task_detail_shared_task(self, second_authenticated_client, shared_task):
        response = second_authenticated_client.get(f'/api/tasks/{shared_task.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == shared_task.id
        assert response.data['title'] == shared_task.title

    def test_get_task_not_found(self, authenticated_client):
        response = authenticated_client.get('/api/tasks/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data

    def test_update_own_task(self, authenticated_client, sample_task):
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

    def test_update_shared_task_forbidden(self, second_authenticated_client, shared_task):
        update_data = {
            'title': 'Tentativa de Atualização',
            'priority': 'urgent'
        }
        response = second_authenticated_client.put(f'/api/tasks/{shared_task.id}/', update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
        assert 'proprietário' in response.data['error']

    def test_delete_own_task(self, authenticated_client, sample_task):
        task_id = sample_task.id
        response = authenticated_client.delete(f'/api/tasks/{task_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task_id).exists()

    def test_delete_shared_task_forbidden(self, second_authenticated_client, shared_task):
        response = second_authenticated_client.delete(f'/api/tasks/{shared_task.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
        assert 'proprietário' in response.data['error']

@pytest.mark.django_db
class TestTaskToggleComplete:
    def test_toggle_complete_own_task(self, authenticated_client, sample_task):
        assert not sample_task.is_completed
        response = authenticated_client.patch(f'/api/tasks/{sample_task.id}/toggle/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_completed'] is True
        assert response.data['status'] == 'completed'
        sample_task.refresh_from_db()
        assert sample_task.is_completed
        assert sample_task.status == 'completed'
        assert sample_task.completed_at is not None

    def test_toggle_uncomplete_own_task(self, authenticated_client, test_user):
        completed_task = Task.objects.create(
            owner=test_user,
            title='Tarefa Concluída',
            status='completed',
            is_completed=True,
            completed_at=timezone.now()
        )
        response = authenticated_client.patch(f'/api/tasks/{completed_task.id}/toggle/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_completed'] is False
        assert response.data['status'] == 'pending'
        completed_task.refresh_from_db()
        assert not completed_task.is_completed
        assert completed_task.status == 'pending'
        assert completed_task.completed_at is None

    def test_toggle_complete_shared_task_forbidden(self, second_authenticated_client, shared_task):
        response = second_authenticated_client.patch(f'/api/tasks/{shared_task.id}/toggle/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
        assert 'proprietário' in response.data['error']
        assert 'status de conclusão' in response.data['error']

@pytest.mark.django_db
class TestTaskSharingAPI:
    def test_get_shared_users_empty(self, authenticated_client, sample_task):
        response = authenticated_client.get(f'/api/tasks/{sample_task.id}/shared-users/')
        assert response.status_code == status.HTTP_200_OK
        assert 'shared_users' in response.data
        assert 'owner' in response.data
        assert 'current_user_is_owner' in response.data
        assert len(response.data['shared_users']) == 0
        assert response.data['current_user_is_owner'] is True
        assert response.data['owner']['email'] == sample_task.owner.email

    def test_get_shared_users_with_sharing(self, authenticated_client, shared_task):
        response = authenticated_client.get(f'/api/tasks/{shared_task.id}/shared-users/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['shared_users']) == 1
        assert response.data['shared_users'][0]['email'] == 'test2@example.com'
        assert response.data['current_user_is_owner'] is True

    def test_get_shared_users_as_shared_user(self, second_authenticated_client, shared_task):
        response = second_authenticated_client.get(f'/api/tasks/{shared_task.id}/shared-users/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['current_user_is_owner'] is False
        assert response.data['owner']['email'] == 'test@example.com'

    def test_share_task_with_user(self, authenticated_client, sample_task, second_test_user):
        share_data = {
            'email': second_test_user.email
        }
        response = authenticated_client.post(f'/api/tasks/{sample_task.id}/shared-users/', share_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == second_test_user.email
        sample_task.refresh_from_db()
        assert sample_task.is_shared_with(second_test_user)

    def test_share_task_with_nonexistent_user(self, authenticated_client, sample_task):
        share_data = {
            'email': 'inexistente@example.com'
        }
        response = authenticated_client.post(f'/api/tasks/{sample_task.id}/shared-users/', share_data)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
        assert 'error' in response.data
        if response.status_code == status.HTTP_404_NOT_FOUND:
            assert 'não encontrado' in response.data['error']
        elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            assert 'erro' in response.data['error'].lower()

    def test_share_task_with_owner(self, authenticated_client, sample_task, test_user):
        share_data = {
            'email': test_user.email
        }
        response = authenticated_client.post(f'/api/tasks/{sample_task.id}/shared-users/', share_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'próprio dono' in response.data['error']

    def test_share_task_already_shared(self, authenticated_client, shared_task, second_test_user):
        share_data = {
            'email': second_test_user.email
        }
        response = authenticated_client.post(f'/api/tasks/{shared_task.id}/shared-users/', share_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'já está compartilhada' in response.data['error']

    def test_share_task_not_owner(self, second_authenticated_client, sample_task, test_user):
        share_data = {
            'email': 'outro@example.com'
        }
        response = second_authenticated_client.post(f'/api/tasks/{sample_task.id}/shared-users/', share_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_user_from_share(self, authenticated_client, shared_task, second_test_user):
        remove_data = {
            'user_id': second_test_user.id
        }
        response = authenticated_client.post(f'/api/tasks/{shared_task.id}/remove-user/', remove_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        shared_task.refresh_from_db()
        assert not shared_task.is_shared_with(second_test_user)

    def test_remove_user_not_shared(self, authenticated_client, sample_task, second_test_user):
        remove_data = {
            'user_id': second_test_user.id
        }
        response = authenticated_client.post(f'/api/tasks/{sample_task.id}/remove-user/', remove_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'não está compartilhado' in response.data['error']

@pytest.mark.django_db
class TestValidationAPI:
    def test_title_required(self, authenticated_client):
        data = {
            'description': 'Descrição sem título'
        }
        response = authenticated_client.post('/api/tasks/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data

    def test_invalid_priority(self, authenticated_client):
        data = {
            'title': 'Tarefa',
            'priority': 'super_urgent'
        }
        response = authenticated_client.post('/api/tasks/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'priority' in response.data

    def test_invalid_status(self, authenticated_client):
        data = {
            'title': 'Tarefa',
            'status': 'maybe_done'
        }
        response = authenticated_client.post('/api/tasks/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'status' in response.data

    def test_valid_due_date_format(self, authenticated_client):
        data = {
            'title': 'Tarefa com data',
            'due_date': '2024-12-31T23:59:59Z'
        }
        response = authenticated_client.post('/api/tasks/', data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_invalid_due_date_format(self, authenticated_client):
        data = {
            'title': 'Tarefa com data inválida',
            'due_date': 'invalid-date'
        }
        response = authenticated_client.post('/api/tasks/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'due_date' in response.data

@pytest.mark.django_db 
class TestTaskOrdering:
    def test_ordering_by_created_at(self, authenticated_client, test_user):
        task1 = Task.objects.create(owner=test_user, title='Primeira tarefa')
        task2 = Task.objects.create(owner=test_user, title='Segunda tarefa')
        response = authenticated_client.get('/api/tasks/?ordering=created_at')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['id'] == task1.id
        assert response.data['results'][1]['id'] == task2.id
        response = authenticated_client.get('/api/tasks/?ordering=-created_at')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['id'] == task2.id
        assert response.data['results'][1]['id'] == task1.id

    def test_ordering_by_priority(self, authenticated_client, test_user):
        Task.objects.create(owner=test_user, title='Baixa', priority='low')
        Task.objects.create(owner=test_user, title='Alta', priority='high')
        Task.objects.create(owner=test_user, title='Urgente', priority='urgent')
        Task.objects.create(owner=test_user, title='Média', priority='medium')
        response = authenticated_client.get('/api/tasks/?ordering=priority')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 4

@pytest.mark.django_db
class TestPagination:
    def test_pagination_structure(self, authenticated_client, test_user):
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
        for i in range(25):
            Task.objects.create(owner=test_user, title=f'Tarefa {i}')
        response = authenticated_client.get('/api/tasks/')
        assert len(response.data['results']) <= 20
        assert response.data['next'] is not None
        assert response.data['previous'] is None
        response = authenticated_client.get('/api/tasks/?page=2')
        assert len(response.data['results']) <= 20
        assert response.data['previous'] is not None

@pytest.mark.django_db
class TestTaskModelMethods:
    def test_share_with_user(self, test_user, second_test_user):
        task = Task.objects.create(owner=test_user, title='Teste')
        task.share_with_user(second_test_user)
        assert task.is_shared_with(second_test_user)
        assert second_test_user in task.get_shared_users()

    def test_unshare_with_user(self, test_user, second_test_user):
        task = Task.objects.create(owner=test_user, title='Teste')
        task.share_with_user(second_test_user)
        task.unshare_with_user(second_test_user)
        assert not task.is_shared_with(second_test_user)
        assert second_test_user not in task.get_shared_users()

    def test_get_all_users_with_access(self, test_user, second_test_user):
        task = Task.objects.create(owner=test_user, title='Teste')
        task.share_with_user(second_test_user)
        users_with_access = task.get_all_users_with_access()
        assert test_user in users_with_access
        assert second_test_user in users_with_access
        assert users_with_access.count() == 2

    def test_is_overdue_property(self, test_user):
        overdue_task = Task.objects.create(
            owner=test_user,
            title='Vencida',
            due_date=timezone.now() - timedelta(days=1)
        )
        assert overdue_task.is_overdue
        future_task = Task.objects.create(
            owner=test_user,
            title='Futura',
            due_date=timezone.now() + timedelta(days=1)
        )
        assert not future_task.is_overdue
        completed_task = Task.objects.create(
            owner=test_user,
            title='Concluída',
            due_date=timezone.now() - timedelta(days=1),
            status='completed',
            is_completed=True
        )
        assert not completed_task.is_overdue

    def test_get_tags_list(self, test_user):
        task = Task.objects.create(
            owner=test_user,
            title='Com tags',
            tags='tag1, tag2, tag3'
        )
        tags = task.get_tags_list()
        assert tags == ['tag1', 'tag2', 'tag3']
        task.tags = ''
        tags = task.get_tags_list()
        assert tags == []

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
