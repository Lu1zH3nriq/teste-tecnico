from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Task
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskListSerializer
)


@swagger_auto_schema(
    methods=['get'],
    operation_summary="Listar tarefas do usuário",
    operation_description="Retorna lista paginada das tarefas do usuário autenticado com filtros opcionais",
    manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, description="Filtrar por status (pending, in_progress, completed, cancelled)", type=openapi.TYPE_STRING),
        openapi.Parameter('priority', openapi.IN_QUERY, description="Filtrar por prioridade (low, medium, high, urgent)", type=openapi.TYPE_STRING),
        openapi.Parameter('search', openapi.IN_QUERY, description="Buscar no título, descrição ou tags", type=openapi.TYPE_STRING),
        openapi.Parameter('ordering', openapi.IN_QUERY, description="Ordenação (-created_at, title, due_date, priority)", type=openapi.TYPE_STRING),
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
        
        status_filter = request.GET.get('status')
        priority_filter = request.GET.get('priority')
        search = request.GET.get('search')
        
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        ordering = request.GET.get('ordering', '-created_at')
        tasks = tasks.order_by(ordering)
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
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
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='post',
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
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_toggle_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    
    if task.is_completed:
        task.status = 'pending'
    else:
        task.status = 'completed'
    
    task.save()
    
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
