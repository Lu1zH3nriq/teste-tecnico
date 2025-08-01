import logging
from typing import Dict, Any, Optional
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
from django.conf import settings

logger = logging.getLogger(__name__)


class CosmosDBConfig:
    
    def __init__(self):
        self.endpoint = getattr(settings, 'COSMOS_ENDPOINT', None)
        self.key = getattr(settings, 'COSMOS_KEY', None)
        self.database_name = getattr(settings, 'COSMOS_DATABASE', 'tasks')
        self.container_name = getattr(settings, 'COSMOS_CONTAINER', 'tasks-manager')

        self.connection_policy = getattr(settings, 'COSMOS_CONNECTION_POLICY', {
            'enable_endpoint_discovery': True,
            'connection_mode': 'Direct',  
            'enable_tcp_over_https': True,  
            'max_connection_pool_size': 50,
            'request_timeout': 10,
            'connection_timeout': 5,
            'retry_total': 3,
            'retry_backoff_factor': 0.3,
        })
        
        self._client = None
        self._database = None
        self._container = None
    
    @property
    def client(self) -> Optional[CosmosClient]:
        
        if not self._client and self.endpoint and self.key:
            try:
                self._client = CosmosClient(
                    self.endpoint,
                    self.key,
                    **self.connection_policy
                )
                logger.info("CosmosDB client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize CosmosDB client: {e}")
                return None
        
        return self._client
    
    @property
    def database(self):
        if not self._database and self.client:
            try:
                self._database = self.client.get_database_client(self.database_name)
                logger.info(f"Connected to database: {self.database_name}")
            except Exception as e:
                logger.error(f"Failed to connect to database {self.database_name}: {e}")
                return None
        
        return self._database
    
    @property
    def container(self):
        if not self._container and self.database:
            try:
                self._container = self.database.get_container_client(self.container_name)
                logger.info(f"Connected to container: {self.container_name}")
            except Exception as e:
                logger.error(f"Failed to connect to container {self.container_name}: {e}")
                return None
        
        return self._container
    
    def create_database_and_container(self) -> bool:
        
        if not self.client:
            logger.error("CosmosDB client not available")
            return False
        
        try:

            database = self.client.create_database_if_not_exists(
                id=self.database_name,
                offer_throughput=400  
            )
            logger.info(f"Database '{self.database_name}' ready")
            

            container_definition = {
                'id': self.container_name,
                'partitionKey': {
                    'paths': ['/user_id'],
                    'kind': 'Hash'
                },
                
                'indexingPolicy': {
                    'indexingMode': 'consistent',
                    'automatic': True,
                    'includedPaths': [
                        {'path': '/user_id/?'},      
                        {'path': '/status/?'},     
                        {'path': '/priority/?'}, 
                        {'path': '/due_date/?'},  
                        {'path': '/created_at/?'},   
                        {'path': '/updated_at/?'},  
                        {'path': '/tags/?'},      
                    ],
                    'excludedPaths': [
                        {'path': '/description/*'}, 
                        {'path': '/_etag/*'},      
                    ]
                },
               
                'defaultTtl': -1  
            }
            

            database.create_container_if_not_exists(
                body=container_definition,
                offer_throughput=400  
            )
            logger.info(f"Container '{self.container_name}' ready with partition key '/user_id'")
            
            return True
            
        except CosmosHttpResponseError as e:
            logger.error(f"CosmosDB HTTP error: {e.message}")
            return False
        except Exception as e:
            logger.error(f"Failed to create database/container: {e}")
            return False
    
    def test_connection(self) -> Dict[str, Any]:
        
        status = {
            'connected': False,
            'endpoint': self.endpoint,
            'database': self.database_name,
            'container': self.container_name,
            'error': None
        }
        
        try:
            if not self.client:
                status['error'] = 'Client initialization failed'
                return status
            
          
            database_info = self.client.get_database_client(self.database_name)
            database_properties = database_info.read()
            
           
            container_info = database_info.get_container_client(self.container_name)
            container_properties = container_info.read()
            
            status.update({
                'connected': True,
                'database_properties': {
                    'id': database_properties.get('id'),
                    'rid': database_properties.get('_rid'),
                },
                'container_properties': {
                    'id': container_properties.get('id'),
                    'partition_key': container_properties.get('partitionKey'),
                    'indexing_policy': container_properties.get('indexingPolicy', {}).get('indexingMode'),
                }
            })
            
            logger.info("CosmosDB connection test successful")
            
        except CosmosResourceNotFoundError as e:
            status['error'] = f'Resource not found: {e.message}'
            logger.warning(f"CosmosDB resource not found: {e.message}")
        except CosmosHttpResponseError as e:
            status['error'] = f'HTTP error: {e.message}'
            logger.error(f"CosmosDB HTTP error: {e.message}")
        except Exception as e:
            status['error'] = f'Connection error: {str(e)}'
            logger.error(f"CosmosDB connection test failed: {e}")
        
        return status



cosmos_config = CosmosDBConfig()


def get_cosmos_container():
    
    return cosmos_config.container


def initialize_cosmosdb():
    
    logger.info("Initializing CosmosDB...")
    
    if not cosmos_config.endpoint or not cosmos_config.key:
        logger.warning("CosmosDB credentials not configured. Skipping initialization.")
        return False
    
    success = cosmos_config.create_database_and_container()
    if success:
        logger.info("CosmosDB initialization completed successfully")
    else:
        logger.error("CosmosDB initialization failed")
    
    return success
