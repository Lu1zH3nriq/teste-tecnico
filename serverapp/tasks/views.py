from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
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
from .cosmos_models import get_cosmos_task_manager

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
        tasks = Task.objects.filter(owner=request.user)
        
        # Filtros básicos
        status_filter = request.GET.get('status')
        priority_filter = request.GET.get('priority')
        search = request.GET.get('search')
        
        # Filtros de data
        due_date_from = request.GET.get('due_date_from')
        due_date_to = request.GET.get('due_date_to')
        overdue_filter = request.GET.get('overdue')
        
        # Aplicar filtros
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        if search:
            # Buscar apenas no título
            tasks = tasks.filter(title__icontains=search)
        
        # Filtros de data
        if due_date_from:
            try:
                from datetime import datetime
                date_from = datetime.strptime(due_date_from, '%Y-%m-%d').date()
                tasks = tasks.filter(due_date__gte=date_from)
            except ValueError:
                pass  # Ignora formato inválido
        
        if due_date_to:
            try:
                from datetime import datetime
                date_to = datetime.strptime(due_date_to, '%Y-%m-%d').date()
                tasks = tasks.filter(due_date__lte=date_to)
            except ValueError:
                pass  # Ignora formato inválido
        
        # Filtro de tarefas atrasadas
        if overdue_filter and overdue_filter.lower() == 'true':
            now = timezone.now().date()
            tasks = tasks.filter(due_date__lt=now, status__in=['pending', 'in_progress'])
        
        ordering = request.GET.get('ordering', '-created_at')
        tasks = tasks.order_by(ordering)
        
        # Debug: verificar quantos registros existem após filtros
        total_tasks = tasks.count()
        logger.info(f"Total tasks after filters: {total_tasks}")
        
        # Aplicar paginação manual
        from django.core.paginator import Paginator, EmptyPage
        from django.http import Http404
        
        # Permitir que o frontend defina o page_size, com fallback para 20
        page_size = request.GET.get('page_size', 20)
        try:
            page_size = int(page_size)
            # Limitar o page_size máximo para evitar sobrecarga
            page_size = min(page_size, 1000)
        except (ValueError, TypeError):
            page_size = 20
        
        # Paginação manual com controle total
        page_number = request.GET.get('page', 1)
        try:
            page_number = int(page_number)
        except (ValueError, TypeError):
            page_number = 1
            
        paginator = Paginator(tasks, page_size)
        
        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            # Se a página não existe, retornar 404
            raise Http404("Página inválida.")
        
        # Serializar os resultados
        serializer = TaskListSerializer(page_obj.object_list, many=True)
        
        # Construir resposta paginada manualmente
        response_data = {
            'count': paginator.count,
            'next': None,
            'previous': None,
            'results': serializer.data
        }
        
        # Adicionar link para próxima página se existir
        if page_obj.has_next():
            next_page = page_obj.next_page_number()
            next_url = request.build_absolute_uri(request.path)
            params = request.GET.copy()
            params['page'] = next_page
            response_data['next'] = f"{next_url}?{params.urlencode()}"
        
        # Adicionar link para página anterior se existir
        if page_obj.has_previous():
            prev_page = page_obj.previous_page_number()
            prev_url = request.build_absolute_uri(request.path)
            params = request.GET.copy()
            params['page'] = prev_page
            response_data['previous'] = f"{prev_url}?{params.urlencode()}"
        
        return Response(response_data)
    
    elif request.method == 'POST':
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(owner=request.user)
            
            cosmos_manager = get_cosmos_task_manager()
            cosmos_task_data = {
                'id': str(task.id),
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'status': task.status,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'is_completed': task.is_completed,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'tags': task.tags,
                'owner_id': str(request.user.id),
                'owner_email': request.user.email,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            }
            
            try:
                cosmos_manager.create_task(cosmos_task_data)
            except Exception as e:
                logger.error(f"Failed to save task to Cosmos DB: {str(e)}")
            
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
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = TaskUpdateSerializer(
            task,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            task = serializer.save()
            
            cosmos_manager = get_cosmos_task_manager()
            cosmos_task_data = {
                'id': str(task.id),
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'status': task.status,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'is_completed': task.is_completed,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'tags': task.tags,
                'owner_id': str(request.user.id),
                'owner_email': request.user.email,
                'updated_at': task.updated_at.isoformat()
            }
            
            try:
                cosmos_manager.update_task(str(task.id), cosmos_task_data)
            except Exception as e:
                logger.error(f"Failed to update task in Cosmos DB: {str(e)}")
            
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        cosmos_manager = get_cosmos_task_manager()
        try:
            cosmos_manager.delete_task(str(task.id), str(request.user.id))
        except Exception as e:
            logger.error(f"Failed to delete task from Cosmos DB: {str(e)}")
        
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
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    
    if task.is_completed:
        task.status = 'pending'
        task.is_completed = False
        task.completed_at = None
    else:
        task.status = 'completed'
        task.is_completed = True
        task.completed_at = timezone.now()
    
    task.save()
    
    cosmos_manager = get_cosmos_task_manager()
    cosmos_task_data = {
        'id': str(task.id),
        'title': task.title,
        'description': task.description,
        'priority': task.priority,
        'status': task.status,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'is_completed': task.is_completed,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'tags': task.tags,
        'owner_id': str(request.user.id),
        'owner_email': request.user.email,
        'updated_at': task.updated_at.isoformat()
    }
    
    try:
        cosmos_manager.update_task(str(task.id), cosmos_task_data)
    except Exception as e:
        logger.error(f"Failed to update task in Cosmos DB: {str(e)}")
    
    serializer = TaskSerializer(task)
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
    user_tasks = Task.objects.filter(owner=request.user)
    
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(is_completed=True).count()
    pending_tasks = user_tasks.filter(status='pending').count()
    in_progress_tasks = user_tasks.filter(status='in_progress').count()
    overdue_tasks = sum(1 for task in user_tasks if task.is_overdue)
    
    high_priority = user_tasks.filter(priority='high').count()
    medium_priority = user_tasks.filter(priority='medium').count()
    low_priority = user_tasks.filter(priority='low').count()
    urgent_priority = user_tasks.filter(priority='urgent').count()
    
    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'overdue_tasks': overdue_tasks,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        'priority_breakdown': {
            'urgent': urgent_priority,
            'high': high_priority,
            'medium': medium_priority,
            'low': low_priority,
        }
    }
    
    return Response(stats)
