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
        self.tasks_container_name = "tasks"
        
        if self.key:
            self.client = CosmosClient(self.endpoint, self.key)
        else:
            credential = DefaultAzureCredential()
            self.client = CosmosClient(self.endpoint, credential)
        
        self.database = None
        self.users_container = None
        self.tasks_container = None
        self._initialize_database()
    
    def _initialize_database(self):
        try:
            self.database = self.client.create_database_if_not_exists(
                id=self.database_name
            )
            logger.info(f"Database '{self.database_name}' initialized successfully")
            
            self.users_container = self.database.create_container_if_not_exists(
                id=self.users_container_name,
                partition_key=PartitionKey(path="/id")
            )
            logger.info(f"Container '{self.users_container_name}' initialized successfully")
            
            # Inicializar container de tarefas
            self.tasks_container = self.database.create_container_if_not_exists(
                id=self.tasks_container_name,
                partition_key=PartitionKey(path="/owner_id")
            )
            logger.info(f"Container '{self.tasks_container_name}' initialized successfully")
            
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

    # ==================== TASK METHODS ====================
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova tarefa no Cosmos DB"""
        try:
            if 'id' not in task_data:
                raise ValueError("Task data must include 'id' field")
            
            if 'owner_id' not in task_data:
                raise ValueError("Task data must include 'owner_id' field")
            
            task_data['type'] = 'task'
            task_data['_entity_type'] = 'Task'
            
            created_task = self.tasks_container.create_item(body=task_data)
            logger.info(f"Task created successfully: {task_data['id']}")
            
            return created_task
            
        except exceptions.CosmosHttpResponseError as e:
            if e.status_code == 409:
                logger.warning(f"Task already exists: {task_data['id']}")
                raise ValueError("Task with this ID already exists")
            else:
                logger.error(f"Failed to create task: {e.message}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error creating task: {str(e)}")
            raise
    
    def get_task_by_id(self, task_id: str, owner_id: str) -> Optional[Dict[str, Any]]:
        """Busca uma tarefa por ID e proprietário"""
        try:
            task = self.tasks_container.read_item(
                item=task_id,
                partition_key=owner_id
            )
            return task
            
        except exceptions.CosmosResourceNotFoundError:
            logger.info(f"Task not found: {task_id} for owner: {owner_id}")
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to get task {task_id}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting task: {str(e)}")
            raise
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza uma tarefa existente"""
        try:
            # Primeiro, busca a tarefa existente
            existing_task = self.get_task_by_id(task_id, task_data.get('owner_id'))
            if not existing_task:
                raise ValueError(f"Task {task_id} not found")
            
            # Atualiza os campos
            existing_task.update(task_data)
            existing_task['updated_at'] = task_data.get('updated_at')
            
            updated_task = self.tasks_container.replace_item(
                item=task_id,
                body=existing_task
            )
            logger.info(f"Task updated successfully: {task_id}")
            
            return updated_task
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update task {task_id}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating task: {str(e)}")
            raise
    
    def delete_task(self, task_id: str, owner_id: str) -> bool:
        """Deleta uma tarefa"""
        try:
            self.tasks_container.delete_item(
                item=task_id,
                partition_key=owner_id
            )
            logger.info(f"Task deleted successfully: {task_id}")
            return True
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Task not found for deletion: {task_id}")
            return False
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete task {task_id}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting task: {str(e)}")
            raise
    
    def list_tasks(self, owner_id: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Lista tarefas de um usuário com filtros opcionais"""
        try:
            # Query básica
            query = "SELECT * FROM c WHERE c.owner_id = @owner_id AND c.type = 'task'"
            parameters = [{"name": "@owner_id", "value": owner_id}]
            
            # Adiciona filtros se fornecidos
            if filters:
                if filters.get('status'):
                    query += " AND c.status = @status"
                    parameters.append({"name": "@status", "value": filters['status']})
                
                if filters.get('priority'):
                    query += " AND c.priority = @priority"
                    parameters.append({"name": "@priority", "value": filters['priority']})
                
                if filters.get('search'):
                    query += " AND (CONTAINS(LOWER(c.title), LOWER(@search)) OR CONTAINS(LOWER(c.description), LOWER(@search)) OR CONTAINS(LOWER(c.tags), LOWER(@search)))"
                    parameters.append({"name": "@search", "value": filters['search']})
            
            # Adiciona ordenação
            ordering = filters.get('ordering', '-created_at') if filters else '-created_at'
            if ordering.startswith('-'):
                field = ordering[1:]
                query += f" ORDER BY c.{field} DESC"
            else:
                query += f" ORDER BY c.{ordering} ASC"
            
            tasks = list(self.tasks_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=False,
                partition_key=owner_id
            ))
            
            logger.info(f"Found {len(tasks)} tasks for owner: {owner_id}")
            return tasks
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to list tasks for owner {owner_id}: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing tasks: {str(e)}")
            raise


cosmos_service = None

def get_cosmos_service() -> CosmosDBService:
    global cosmos_service
    
    if cosmos_service is None:
        cosmos_service = CosmosDBService()
    
    return cosmos_service


def is_cosmos_configured() -> bool:
    return bool(settings.COSMOS_ENDPOINT and (settings.COSMOS_KEY or True))
