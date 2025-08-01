from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction, IntegrityError
from .cosmos_models import UserService, CosmosUser
from core.cosmos_service import is_cosmos_configured
import re
import logging

logger = logging.getLogger(__name__)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Senha deve ter pelo menos 6 caracteres."
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirme sua senha."
    )
    email = serializers.EmailField(
        required=True,
        help_text="Email válido e único."
    )
    first_name = serializers.CharField(
        required=True,
        max_length=30,
        help_text="Nome (obrigatório)."
    )
    last_name = serializers.CharField(
        required=True,
        max_length=30,
        help_text="Sobrenome (obrigatório)."
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password', 'first_name', 'last_name')

    def validate_email(self, value):
        email = value.lower().strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise serializers.ValidationError("Formato de email inválido.")
        if len(email) > 254:
            raise serializers.ValidationError("Email muito longo.")
        if email.startswith('.') or email.endswith('.'):
            raise serializers.ValidationError("Email não pode começar ou terminar com ponto.")
        if '..' in email:
            raise serializers.ValidationError("Email não pode conter pontos consecutivos.")
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        if User.objects.filter(username__iexact=email).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return email

    def validate_first_name(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Nome é obrigatório.")
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value):
            raise serializers.ValidationError("Nome deve conter apenas letras.")
        return value.strip().title()

    def validate_last_name(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Sobrenome é obrigatório.")
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value):
            raise serializers.ValidationError("Sobrenome deve conter apenas letras.")
        return value.strip().title()

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Senha deve ter pelo menos 6 caracteres.")
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        email = attrs.get('email')
        if password != confirm_password:
            raise serializers.ValidationError("Senhas não coincidem.")
        if email and User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({
                "email": ["Este email já está em uso."]
            })
        attrs.pop('confirm_password', None)
        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        try:
            with transaction.atomic():
                if User.objects.filter(email__iexact=email).exists():
                    raise serializers.ValidationError({
                        "email": ["Este email já está em uso."]
                    })
                if User.objects.filter(username__iexact=email).exists():
                    raise serializers.ValidationError({
                        "email": ["Este email já está em uso."]
                    })
                result = UserService.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                django_user = result['django_user']
                if result.get('cosmos_user'):
                    logger.info(f"User created in both Django and Cosmos DB: {email}")
                else:
                    logger.info(f"User created in Django only (Cosmos DB not configured): {email}")
                return django_user
        except IntegrityError as e:
            logger.error(f"Database integrity error during user creation: {str(e)}")
            raise serializers.ValidationError({
                "email": ["Este email já está em uso."]
            })
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            if "email" in str(e).lower() and "unique" in str(e).lower():
                raise serializers.ValidationError({
                    "email": ["Este email já está em uso."]
                })
            raise serializers.ValidationError(f"Erro ao criar usuário: {str(e)}")


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, 
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password', '')
        if not email or not password:
            raise serializers.ValidationError("Email e senha são obrigatórios.")
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Credenciais inválidas.")
        if not user.is_active:
            raise serializers.ValidationError("Conta desativada.")
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Nova senha deve ter pelo menos 6 caracteres.")
        if value.isdigit():
            raise serializers.ValidationError("Nova senha não pode ser apenas números.")
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError("Nova senha e confirmação não coincidem.")
        current_password = attrs.get('current_password')
        if new_password == current_password:
            raise serializers.ValidationError("Nova senha deve ser diferente da atual.")
        return attrs
