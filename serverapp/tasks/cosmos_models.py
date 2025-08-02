import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from core.cosmos_service import get_cosmos_service, is_cosmos_configured
import logging

logger = logging.getLogger(__name__)


class CosmosTask:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.priority = kwargs.get('priority', 'medium')
        self.status = kwargs.get('status', 'pending')
        self.due_date = kwargs.get('due_date', None)
        self.is_completed = kwargs.get('is_completed', False)
        self.completed_at = kwargs.get('completed_at', None)
        self.tags = kwargs.get('tags', '')
        self.owner_id = kwargs.get('owner_id', '')
        self.owner_email = kwargs.get('owner_email', '')
        self.created_at = kwargs.get('created_at', datetime.utcnow().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow().isoformat())
        self.type = 'task'
        self._entity_type = 'Task'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at,
            'tags': self.tags,
            'owner_id': self.owner_id,
            'owner_email': self.owner_email,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'type': self.type,
            '_entity_type': self._entity_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CosmosTask':
        return cls(**data)


class CosmosTaskManager:
    def __init__(self):
        self.cosmos_service = get_cosmos_service()
        
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova tarefa no Cosmos DB"""
        try:
            if not is_cosmos_configured():
                logger.warning("Cosmos DB not configured, skipping task creation")
                return None
                
            # Cria o objeto da tarefa
            cosmos_task = CosmosTask(**task_data)
            
            # Salva no Cosmos DB
            result = self.cosmos_service.create_task(cosmos_task.to_dict())
            logger.info(f"Task created in Cosmos DB: {cosmos_task.id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating task in Cosmos DB: {str(e)}")
            return None
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza uma tarefa no Cosmos DB"""
        try:
            if not is_cosmos_configured():
                logger.warning("Cosmos DB not configured, skipping task update")
                return None
                
            # Adiciona timestamp de atualização
            task_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.cosmos_service.update_task(task_id, task_data)
            logger.info(f"Task updated in Cosmos DB: {task_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating task in Cosmos DB: {str(e)}")
            return None
    
    def delete_task(self, task_id: str, owner_id: str) -> bool:
        """Deleta uma tarefa do Cosmos DB"""
        try:
            if not is_cosmos_configured():
                logger.warning("Cosmos DB not configured, skipping task deletion")
                return False
                
            result = self.cosmos_service.delete_task(task_id, owner_id)
            logger.info(f"Task deleted from Cosmos DB: {task_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting task from Cosmos DB: {str(e)}")
            return False
    
    def get_task_by_id(self, task_id: str, owner_id: str) -> Optional[Dict[str, Any]]:
        """Busca uma tarefa específica no Cosmos DB"""
        try:
            if not is_cosmos_configured():
                return None
                
            return self.cosmos_service.get_task_by_id(task_id, owner_id)
            
        except Exception as e:
            logger.error(f"Error getting task from Cosmos DB: {str(e)}")
            return None
    
    def list_tasks(self, owner_id: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Lista tarefas do usuário no Cosmos DB"""
        try:
            if not is_cosmos_configured():
                return []
                
            return self.cosmos_service.list_tasks(owner_id, filters or {})
            
        except Exception as e:
            logger.error(f"Error listing tasks from Cosmos DB: {str(e)}")
            return []


# Instância global do manager
cosmos_task_manager = CosmosTaskManager()


def get_cosmos_task_manager() -> CosmosTaskManager:
    """Retorna a instância global do task manager"""
    return cosmos_task_manager
