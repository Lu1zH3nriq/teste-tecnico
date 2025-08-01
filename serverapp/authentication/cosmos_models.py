import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from core.cosmos_service import get_cosmos_service, is_cosmos_configured
import logging

logger = logging.getLogger(__name__)


class CosmosUser:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.username = kwargs.get('username', '')
        self.email = kwargs.get('email', '')
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.password_hash = kwargs.get('password_hash', '')
        self.is_active = kwargs.get('is_active', True)
        self.is_staff = kwargs.get('is_staff', False)
        self.is_superuser = kwargs.get('is_superuser', False)
        self.date_joined = kwargs.get('date_joined', datetime.utcnow().isoformat())
        self.last_login = kwargs.get('last_login', None)
        self.type = 'user'
        self._entity_type = 'User'
    
    def set_password(self, raw_password: str):
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password_hash)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password_hash': self.password_hash,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser,
            'date_joined': self.date_joined,
            'last_login': self.last_login,
            'type': self.type,
            '_entity_type': self._entity_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CosmosUser':
        return cls(**data)
    
    def save(self) -> 'CosmosUser':
        if not is_cosmos_configured():
            raise ValueError("Cosmos DB is not configured")
        cosmos_service = get_cosmos_service()
        try:
            existing_user = cosmos_service.get_user_by_id(self.id)
            if existing_user:
                updated_data = cosmos_service.update_user(self.id, self.to_dict())
                return self.from_dict(updated_data)
            else:
                created_data = cosmos_service.create_user(self.to_dict())
                return self.from_dict(created_data)
        except Exception as e:
            logger.error(f"Failed to save user to Cosmos DB: {str(e)}")
            raise
    
    @classmethod
    def get_by_id(cls, user_id: str) -> Optional['CosmosUser']:
        if not is_cosmos_configured():
            return None
        cosmos_service = get_cosmos_service()
        user_data = cosmos_service.get_user_by_id(user_id)
        return cls.from_dict(user_data) if user_data else None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['CosmosUser']:
        if not is_cosmos_configured():
            return None
        cosmos_service = get_cosmos_service()
        user_data = cosmos_service.get_user_by_email(email)
        return cls.from_dict(user_data) if user_data else None
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['CosmosUser']:
        if not is_cosmos_configured():
            return None
        cosmos_service = get_cosmos_service()
        try:
            users = cosmos_service.users_container.query_items(
                query="SELECT * FROM c WHERE c.username = @username AND c.type = 'user'",
                parameters=[{"name": "@username", "value": username}],
                enable_cross_partition_query=True
            )
            user_list = list(users)
            return cls.from_dict(user_list[0]) if user_list else None
        except Exception as e:
            logger.error(f"Failed to get user by username: {str(e)}")
            return None
    
    def delete(self) -> bool:
        if not is_cosmos_configured():
            raise ValueError("Cosmos DB is not configured")
        cosmos_service = get_cosmos_service()
        return cosmos_service.delete_user(self.id)
    
    def __str__(self):
        return f"CosmosUser(id={self.id}, email={self.email})"


class UserService:
    @staticmethod
    def create_user(username: str, email: str, password: str, 
                   first_name: str = '', last_name: str = '') -> Dict[str, Any]:
        try:
            if is_cosmos_configured():
                existing_cosmos_user = CosmosUser.get_by_email(email)
                if existing_cosmos_user:
                    raise ValueError("User with this email already exists in Cosmos DB")
            if User.objects.filter(email=email).exists():
                raise ValueError("User with this email already exists in Django")
            if User.objects.filter(username=username).exists():
                raise ValueError("User with this username already exists")
            django_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            cosmos_user = None
            if is_cosmos_configured():
                cosmos_user = CosmosUser(
                    id=str(django_user.id),
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                cosmos_user.set_password(password)
                cosmos_user = cosmos_user.save()
                logger.info(f"User created in Cosmos DB: {email}")
            logger.info(f"User created successfully: {email}")
            return {
                'django_user': django_user,
                'cosmos_user': cosmos_user,
                'success': True,
                'message': 'User created successfully'
            }
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            try:
                if 'django_user' in locals():
                    django_user.delete()
            except:
                pass
            raise
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            try:
                django_user = User.objects.get(email=email)
                if django_user.check_password(password):
                    django_user.save(update_fields=['last_login'])
                    cosmos_user = None
                    if is_cosmos_configured():
                        cosmos_user = CosmosUser.get_by_id(str(django_user.id))
                    return {
                        'django_user': django_user,
                        'cosmos_user': cosmos_user,
                        'authenticated': True
                    }
            except User.DoesNotExist:
                pass
            if is_cosmos_configured():
                cosmos_user = CosmosUser.get_by_email(email)
                if cosmos_user and cosmos_user.check_password(password):
                    return {
                        'django_user': None,
                        'cosmos_user': cosmos_user,
                        'authenticated': True
                    }
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    @staticmethod
    def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        try:
            django_user = None
            try:
                django_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
            cosmos_user = None
            if is_cosmos_configured():
                cosmos_user = CosmosUser.get_by_id(user_id)
            if django_user or cosmos_user:
                return {
                    'django_user': django_user,
                    'cosmos_user': cosmos_user
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            return None
