from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .models import Task
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskListSerializer
)

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    methods=['get'],
    operation_summary="Listar tarefas do usuário",
    operation_description="Retorna lista paginada das tarefas do usuário autenticado com filtros opcionais",
    manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, description="Filtrar por status (pending, in_progress, completed, cancelled)", type=openapi.TYPE_STRING),
        openapi.Parameter('priority', openapi.IN_QUERY, description="Filtrar por prioridade (low, medium, high, urgent)", type=openapi.TYPE_STRING),
        openapi.Parameter('search', openapi.IN_QUERY, description="Buscar no título da tarefa", type=openapi.TYPE_STRING),
        openapi.Parameter('ordering', openapi.IN_QUERY, description="Ordenação (-created_at, title, due_date, priority)", type=openapi.TYPE_STRING),
        openapi.Parameter('due_date_from', openapi.IN_QUERY, description="Filtrar tarefas com vencimento a partir desta data (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        openapi.Parameter('due_date_to', openapi.IN_QUERY, description="Filtrar tarefas com vencimento até esta data (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        openapi.Parameter('overdue', openapi.IN_QUERY, description="Filtrar apenas tarefas atrasadas (true/false)", type=openapi.TYPE_BOOLEAN),
    ],
    responses={
        200: TaskListSerializer(many=True),
        401: openapi.Response(description="Token inválido ou expirado")
    },
    tags=['Tarefas'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    methods=['post'],
    operation_summary="Criar nova tarefa",
    operation_description="Cria uma nova tarefa para o usuário autenticado",
    request_body=TaskCreateSerializer,
    responses={
        201: TaskSerializer,
        400: openapi.Response(description="Dados inválidos"),
        401: openapi.Response(description="Token inválido ou expirado")
    },
    tags=['Tarefas'],
    security=[{'Bearer': []}]
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list_create(request):
    if request.method == 'GET':
        from django.db.models import Q
        queryset = Task.objects.filter(
            Q(owner=request.user) | Q(shared_with=request.user)
        ).distinct()
        status_filter = request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        priority_filter = request.GET.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        due_date_from = request.GET.get('due_date_from')
        if due_date_from:
            try:
                from datetime import datetime
                date_from = datetime.strptime(due_date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__gte=date_from)
            except ValueError:
                pass
        due_date_to = request.GET.get('due_date_to')
        if due_date_to:
            try:
                from datetime import datetime
                date_to = datetime.strptime(due_date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__lte=date_to)
            except ValueError:
                pass
        overdue_filter = request.GET.get('overdue')
        if overdue_filter and overdue_filter.lower() == 'true':
            from datetime import datetime
            now = timezone.now().date()
            queryset = queryset.filter(
                due_date__lt=now,
                status__in=['pending', 'in_progress']
            )
        ordering = request.GET.get('ordering', '-created_at')
        valid_orderings = ['created_at', '-created_at', 'title', '-title', 
                          'due_date', '-due_date', 'priority', '-priority']
        if ordering in valid_orderings:
            if ordering == 'priority' or ordering == '-priority':
                priority_order = {
                    'urgent': 4, 'high': 3, 'medium': 2, 'low': 1
                }
                queryset = sorted(queryset, 
                                key=lambda x: priority_order.get(x.priority, 2),
                                reverse=ordering.startswith('-'))
                task_ids = [task.id for task in queryset]
                queryset = Task.objects.filter(id__in=task_ids)
                if ordering.startswith('-'):
                    task_ids.reverse()
                preserved = models.Case(*[models.When(pk=pk, then=pos) for pos, pk in enumerate(task_ids)])
                queryset = queryset.order_by(preserved)
            else:
                queryset = queryset.order_by(ordering)
        from django.core.paginator import Paginator
        page_size = min(int(request.GET.get('page_size', 20)), 1000)
        paginator = Paginator(queryset, page_size)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        serializer = TaskListSerializer(page_obj, many=True, context={'request': request})
        response_data = {
            'count': paginator.count,
            'next': f"?page={page_obj.next_page_number()}" if page_obj.has_next() else None,
            'previous': f"?page={page_obj.previous_page_number()}" if page_obj.has_previous() else None,
            'results': serializer.data
        }
        return Response(response_data)
    elif request.method == 'POST':
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(owner=request.user)
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=['get'],
    operation_summary="Obter detalhes da tarefa",
    operation_description="Retorna detalhes completos de uma tarefa específica",
    responses={
        200: TaskSerializer,
        404: openapi.Response(description="Tarefa não encontrada"),
        401: openapi.Response(description="Token inválido ou expirado")
    },
    tags=['Tarefas'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    methods=['put'],
    operation_summary="Atualizar tarefa completamente",
    operation_description="Atualiza todos os campos de uma tarefa específica",
    request_body=TaskUpdateSerializer,
    responses={
        200: TaskSerializer,
        400: openapi.Response(description="Dados inválidos"),
        404: openapi.Response(description="Tarefa não encontrada"),
        401: openapi.Response(description="Token inválido ou expirado")
    },
    tags=['Tarefas'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    methods=['patch'],
    operation_summary="Atualizar tarefa parcialmente",
    operation_description="Atualiza campos específicos de uma tarefa",
    request_body=TaskUpdateSerializer,
    responses={
        200: TaskSerializer,
        400: openapi.Response(description="Dados inválidos"),
        404: openapi.Response(description="Tarefa não encontrada"),
        401: openapi.Response(description="Token inválido ou expirado")
    },
    tags=['Tarefas'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    methods=['delete'],
    operation_summary="Excluir tarefa",
    operation_description="Remove uma tarefa específica permanentemente",
    responses={
        204: openapi.Response(description="Tarefa excluída com sucesso"),
        404: openapi.Response(description="Tarefa não encontrada"),
        401: openapi.Response(description="Token inválido ou expirado")
    },
    tags=['Tarefas'],
    security=[{'Bearer': []}]
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail(request, task_id):
    from django.db.models import Q
    try:
        task = Task.objects.get(
            Q(id=task_id) & (Q(owner=request.user) | Q(shared_with=request.user))
        )
    except Task.DoesNotExist:
        return Response(
            {'error': 'Tarefa não encontrada ou você não tem permissão para acessá-la'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    is_owner = task.owner == request.user
    if request.method == 'GET':
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)
    elif request.method in ['PUT', 'PATCH']:
        if not is_owner:
            return Response(
                {'error': 'Apenas o proprietário da tarefa pode modificá-la'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = TaskUpdateSerializer(
            task,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            task = serializer.save()
            response_serializer = TaskSerializer(task, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if not is_owner:
            return Response(
                {'error': 'Apenas o proprietário da tarefa pode deletá-la'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='patch',
    operation_summary="Alternar status de conclusão",
    operation_description="Marca uma tarefa como completa ou incompleta alternadamente",
    responses={
        200: TaskSerializer,
        404: openapi.Response(description="Tarefa não encontrada"),
        401: openapi.Response(description="Token inválido ou expirado")
    },
    tags=['Tarefas'],
    security=[{'Bearer': []}]
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def task_toggle_complete(request, task_id):
    from django.db.models import Q
    try:
        task = Task.objects.get(
            Q(id=task_id) & (Q(owner=request.user) | Q(shared_with=request.user))
        )
    except Task.DoesNotExist:
        return Response(
            {'error': 'Tarefa não encontrada ou você não tem permissão para acessá-la'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    is_owner = task.owner == request.user
    if not is_owner:
        return Response(
            {'error': 'Apenas o proprietário da tarefa pode alterar o status de conclusão'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    if task.is_completed:
        task.status = 'pending'
        task.is_completed = False
        task.completed_at = None
    else:
        task.status = 'completed'
        task.is_completed = True
        task.completed_at = timezone.now()
    task.save()
    serializer = TaskSerializer(task, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_summary="Estatísticas das tarefas",
    operation_description="Retorna estatísticas detalhadas das tarefas do usuário",
    responses={
        200: openapi.Response(
            description="Estatísticas das tarefas",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, description="Total de tarefas"),
                    'completed_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, description="Tarefas concluídas"),
                    'pending_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, description="Tarefas pendentes"),
                    'in_progress_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, description="Tarefas em progresso"),
                    'overdue_tasks': openapi.Schema(type=openapi.TYPE_INTEGER, description="Tarefas em atraso"),
                    'completion_rate': openapi.Schema(type=openapi.TYPE_NUMBER, description="Taxa de conclusão (%)"),
                    'priority_breakdown': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'urgent': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'high': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'medium': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'low': openapi.Schema(type=openapi.TYPE_INTEGER),
                        }
                    )
                }
            )
        ),
        401: openapi.Response(description="Token inválido ou expirado")
    },
    tags=['Estatísticas'],
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_stats(request):
    from django.db.models import Q
    user_tasks = Task.objects.filter(
        Q(owner=request.user) | Q(shared_with=request.user)
    ).distinct()
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(is_completed=True).count()
    pending_tasks = user_tasks.filter(status='pending').count()
    in_progress_tasks = user_tasks.filter(status='in_progress').count()
    overdue_tasks = sum(1 for task in user_tasks if task.is_overdue)
    high_priority = user_tasks.filter(priority='high').count()
    medium_priority = user_tasks.filter(priority='medium').count()
    low_priority = user_tasks.filter(priority='low').count()
    urgent_priority = user_tasks.filter(priority='urgent').count()
    owned_tasks = user_tasks.filter(owner=request.user).count()
    shared_tasks = user_tasks.filter(shared_with=request.user).exclude(owner=request.user).count()
    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'overdue_tasks': overdue_tasks,
        'owned_tasks': owned_tasks,
        'shared_tasks': shared_tasks,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        'priority_breakdown': {
            'urgent': urgent_priority,
            'high': high_priority,
            'medium': medium_priority,
            'low': low_priority,
        }
    }
    return Response(stats)


@swagger_auto_schema(
    methods=['get'],
    operation_summary="Listar usuários compartilhados de uma tarefa",
    operation_description="Retorna lista de usuários que têm acesso à tarefa",
    responses={
        200: openapi.Response(description="Lista de usuários compartilhados"),
        404: openapi.Response(description="Tarefa não encontrada")
    },
    tags=['Compartilhamento'],
    security=[{'Bearer': []}]
)
@swagger_auto_schema(
    methods=['post'],
    operation_summary="Compartilhar tarefa com usuário",
    operation_description="Adiciona um usuário ao compartilhamento da tarefa",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email do usuário')
        },
        required=['email']
    ),
    responses={
        200: openapi.Response(description="Usuário adicionado com sucesso"),
        400: openapi.Response(description="Email inválido ou usuário não encontrado"),
        404: openapi.Response(description="Tarefa não encontrada")
    },
    tags=['Compartilhamento'],
    security=[{'Bearer': []}]
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_shared_users(request, task_id):
    from django.db.models import Q
    try:
        task = Task.objects.get(
            Q(id=task_id) & (Q(owner=request.user) | Q(shared_with=request.user))
        )
    except Task.DoesNotExist:
        return Response(
            {'error': 'Tarefa não encontrada ou você não tem permissão para acessá-la'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    is_owner = task.owner == request.user
    if request.method == 'GET':
        shared_users_queryset = task.get_shared_users()
        shared_users = [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
            for user in shared_users_queryset
        ]
        response_data = {
            'shared_users': shared_users,
            'owner': {
                'id': task.owner.id,
                'first_name': task.owner.first_name,
                'last_name': task.owner.last_name,
                'email': task.owner.email,
                'username': task.owner.username
            },
            'current_user_is_owner': is_owner,
            'task_info': {
                'id': task.id,
                'title': task.title,
                'description': task.description
            }
        }
        return Response(response_data)
    elif request.method == 'POST':
        if not is_owner:
            return Response(
                {'error': 'Apenas o proprietário da tarefa pode adicionar usuários ao compartilhamento'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user_to_share = get_object_or_404(User, email=email)
            if user_to_share == task.owner:
                return Response(
                    {'error': 'Não é possível compartilhar a tarefa com o próprio dono'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            if task.is_shared_with(user_to_share):
                return Response(
                    {'error': 'Tarefa já está compartilhada com este usuário'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            task.share_with_user(user_to_share)
            return Response({
                'message': f'Tarefa compartilhada com {email} com sucesso',
                'user': {
                    'id': user_to_share.id,
                    'first_name': user_to_share.first_name,
                    'last_name': user_to_share.last_name,
                    'email': user_to_share.email
                }
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado com este email'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erro ao compartilhar tarefa: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@swagger_auto_schema(
    methods=['post'],
    operation_summary="Remover usuário do compartilhamento",
    operation_description="Remove um usuário do compartilhamento da tarefa",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do usuário')
        },
        required=['user_id']
    ),
    responses={
        200: openapi.Response(description="Usuário removido com sucesso"),
        400: openapi.Response(description="ID do usuário inválido"),
        404: openapi.Response(description="Tarefa não encontrada")
    },
    tags=['Compartilhamento'],
    security=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_remove_user(request, task_id):
    from django.db.models import Q
    try:
        task = Task.objects.get(
            Q(id=task_id) & (Q(owner=request.user) | Q(shared_with=request.user))
        )
    except Task.DoesNotExist:
        return Response(
            {'error': 'Tarefa não encontrada ou você não tem permissão para acessá-la'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    is_owner = task.owner == request.user
    if not is_owner:
        return Response(
            {'error': 'Apenas o proprietário da tarefa pode remover usuários do compartilhamento'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    user_id = request.data.get('user_id')
    if not user_id:
        return Response(
            {'error': 'ID do usuário é obrigatório'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user_to_remove = get_object_or_404(User, id=user_id)
        if not task.is_shared_with(user_to_remove):
            return Response(
                {'error': 'Usuário não está compartilhado com esta tarefa'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        task.unshare_with_user(user_to_remove)
        return Response({
            'message': 'Usuário removido do compartilhamento com sucesso'
        })
    except Exception as e:
        return Response(
            {'error': f'Erro ao remover usuário: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_share(request, task_id):
    return task_shared_users(request, task_id)
