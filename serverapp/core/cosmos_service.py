import os
import logging
from typing import Dict, Any, Optional, List
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential
from django.conf import settings

logger = logging.getLogger(__name__)


class CosmosDBService:
    
    def __init__(self):
        self.endpoint = settings.COSMOS_ENDPOINT
        self.key = settings.COSMOS_KEY
        self.database_name = settings.COSMOS_DATABASE
        self.users_container_name = "users"
        
        if self.key:
            self.client = CosmosClient(self.endpoint, self.key)
        else:
            credential = DefaultAzureCredential()
            self.client = CosmosClient(self.endpoint, credential)
        
        self.database = None
        self.users_container = None
        self._initialize_database()
    
    def _initialize_database(self):
        try:
            self.database = self.client.create_database_if_not_exists(
                id=self.database_name
            )
            logger.info(f"Database '{self.database_name}' initialized successfully")
            
            self.users_container = self.database.create_container_if_not_exists(
                id=self.users_container_name,
                partition_key=PartitionKey(path="/id"),
                offer_throughput=400
            )
            logger.info(f"Container '{self.users_container_name}' initialized successfully")
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to initialize Cosmos DB: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing Cosmos DB: {str(e)}")
            raise
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if 'id' not in user_data:
                raise ValueError("User data must include 'id' field")
            
            user_data['type'] = 'user'
            user_data['_entity_type'] = 'User'
            created_user = self.users_container.create_item(body=user_data)
            logger.info(f"User created successfully: {user_data.get('email', user_data['id'])}")
            
            return created_user
            
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 409:
                logger.warning(f"User already exists: {user_data.get('email', user_data['id'])}")
                raise ValueError("User with this ID already exists")
            else:
                logger.error(f"Failed to create user: {e.message}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error creating user: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            user = self.users_container.read_item(
                item=user_id,
                partition_key=user_id
            )
            return user
            
        except exceptions.CosmosResourceNotFoundError:
            logger.info(f"User not found: {user_id}")
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get user {user_id}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting user: {str(e)}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            query = "SELECT * FROM c WHERE c.email = @email AND c.type = 'user'"
            parameters = [{"name": "@email", "value": email}]
            
            users = list(self.users_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return users[0] if users else None
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to query user by email {email}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error querying user: {str(e)}")
            raise
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            existing_user = self.get_user_by_id(user_id)
            if not existing_user:
                raise ValueError(f"User not found: {user_id}")
            
            existing_user.update(user_data)
            
            updated_user = self.users_container.replace_item(
                item=user_id,
                body=existing_user
            )
            
            logger.info(f"User updated successfully: {user_id}")
            return updated_user
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update user {user_id}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating user: {str(e)}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        try:
            self.users_container.delete_item(
                item=user_id,
                partition_key=user_id
            )
            
            logger.info(f"User deleted successfully: {user_id}")
            return True
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"User not found for deletion: {user_id}")
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete user {user_id}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting user: {str(e)}")
            raise
    
    def list_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            query = "SELECT * FROM c WHERE c.type = 'user' ORDER BY c._ts DESC"
            
            users = list(self.users_container.query_items(
                query=query,
                enable_cross_partition_query=True,
                max_item_count=limit
            ))
            
            return users
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to list users: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing users: {str(e)}")
            raise


cosmos_service = None

def get_cosmos_service() -> CosmosDBService:
    global cosmos_service
    
    if cosmos_service is None:
        cosmos_service = CosmosDBService()
    
    return cosmos_service


def is_cosmos_configured() -> bool:
    return bool(settings.COSMOS_ENDPOINT and (settings.COSMOS_KEY or True))
