from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer
)

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='post',
    operation_summary="Registrar novo usuário",
    operation_description="Endpoint para registro de novos usuários no sistema",
    request_body=UserRegistrationSerializer,
    responses={
        201: openapi.Response(
            description="Usuário criado com sucesso",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Usuário criado com sucesso"),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                            'username': openapi.Schema(type=openapi.TYPE_STRING, example="usuario123"),
                            'email': openapi.Schema(type=openapi.TYPE_STRING, example="usuario@email.com"),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING, example="João"),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING, example="Silva"),
                        }
                    ),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                }
            )
        ),
        400: openapi.Response(
            description="Dados inválidos",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Dados inválidos"),
                    'errors': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            )
        ),
        500: openapi.Response(description="Erro interno do servidor")
    },
    tags=['Autenticação']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            user_data = UserSerializer(user).data
            
            logger.info(f"Novo usuário registrado: {user.username}")
            
            return Response({
                'message': 'Usuário criado com sucesso',
                'user': user_data,
                'access': str(access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Tentativa de registro com dados inválidos: {serializer.errors}")
        return Response({
            'message': 'Dados inválidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Erro durante o registro: {str(e)}", exc_info=True)
        return Response({
            'message': 'Erro interno do servidor',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_summary="Login de usuário",
    operation_description="Endpoint para autenticação de usuários existentes",
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response(
            description="Login realizado com sucesso",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Login realizado com sucesso"),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                            'username': openapi.Schema(type=openapi.TYPE_STRING, example="usuario123"),
                            'email': openapi.Schema(type=openapi.TYPE_STRING, example="usuario@email.com"),
                        }
                    ),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                }
            )
        ),
        401: openapi.Response(
            description="Credenciais inválidas",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Credenciais inválidas"),
                    'errors': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            )
        ),
        500: openapi.Response(description="Erro interno do servidor")
    },
    tags=['Autenticação']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    try:
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            user_data = UserSerializer(user).data
            
            logger.info(f"Login realizado: {user.username}")
            
            return Response({
                'message': 'Login realizado com sucesso',
                'user': user_data,
                'access': str(access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        
        logger.warning(f"Tentativa de login com credenciais inválidas: {request.data.get('username', 'N/A')}")
        return Response({
            'message': 'Credenciais inválidas',
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)
        
    except Exception as e:
        logger.error(f"Erro durante o login: {str(e)}", exc_info=True)
        return Response({
            'message': 'Erro interno do servidor',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_summary="Logout de usuário",
    operation_description="Endpoint para realizar logout e invalidar o refresh token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Token de refresh para invalidar", example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
        },
        required=['refresh']
    ),
    responses={
        200: openapi.Response(
            description="Logout realizado com sucesso",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Logout realizado com sucesso"),
                }
            )
        ),
        400: openapi.Response(description="Token de refresh é obrigatório"),
        401: openapi.Response(description="Token inválido ou expirado")
    },
    tags=['Autenticação'],
    security=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh_token = request.data.get('refresh')
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"Logout realizado: {request.user.username}")
            
            return Response({
                'message': 'Logout realizado com sucesso'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Token de refresh é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Erro durante o logout: {str(e)}", exc_info=True)
        return Response({
            'message': 'Erro durante o logout',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)