from django.core.management.base import BaseCommand
from core.cosmosdb import cosmos_config, initialize_cosmosdb


class Command(BaseCommand):
    help = 'Setup and test Azure CosmosDB connection for the todolist application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Only test the connection without creating resources',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of container (WARNING: This will delete existing data)',
        )

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.HTTP_INFO('=== Azure CosmosDB Setup and Test ===\n')
        )


        self._display_configuration()


        if not self._test_connection():
            return


        if options['test_only']:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Connection test completed successfully!')
            )
            return


        self._setup_cosmosdb(force=options['force'])

    def _display_configuration(self):

        self.stdout.write(self.style.HTTP_INFO('📋 Current Configuration:'))
        
        config_display = {
            'Endpoint': cosmos_config.endpoint or 'Not configured',
            'Database': cosmos_config.database_name,
            'Container': cosmos_config.container_name,
            'Partition Key': '/user_id (recommended)',
            'Connection Mode': cosmos_config.connection_policy.get('connection_mode', 'Direct'),
        }
        
        for key, value in config_display.items():
            self.stdout.write(f'  • {key}: {self.style.WARNING(value)}')
        
        self.stdout.write('')

    def _test_connection(self):

        self.stdout.write(self.style.HTTP_INFO('🔗 Testing CosmosDB Connection...'))
        
        if not cosmos_config.endpoint:
            self.stdout.write(
                self.style.ERROR('❌ COSMOS_ENDPOINT not configured in environment variables')
            )
            self._display_setup_instructions()
            return False
        
        if not cosmos_config.key:
            self.stdout.write(
                self.style.ERROR('❌ COSMOS_KEY not configured in environment variables')
            )
            self._display_setup_instructions()
            return False
        

        status = cosmos_config.test_connection()
        
        if status['connected']:
            self.stdout.write(self.style.SUCCESS('✅ Connection successful!'))
            

            if 'database_properties' in status:
                db_props = status['database_properties']
                self.stdout.write(f"  • Database ID: {self.style.WARNING(db_props.get('id'))}")
                self.stdout.write(f"  • Database RID: {self.style.WARNING(db_props.get('rid'))}")
            
            if 'container_properties' in status:
                container_props = status['container_properties']
                self.stdout.write(f"  • Container ID: {self.style.WARNING(container_props.get('id'))}")
                
                partition_key = container_props.get('partition_key', {})
                if partition_key:
                    paths = partition_key.get('paths', [])
                    current_pk = paths[0] if paths else 'Not configured'
                    
                    if current_pk == '/user_id':
                        self.stdout.write(f"  • Partition Key: {self.style.SUCCESS(current_pk)} ✅ Optimized!")
                    elif current_pk == '/id':
                        self.stdout.write(f"  • Partition Key: {self.style.ERROR(current_pk)} ⚠️  Not optimal for this workload")
                        self._display_partition_key_warning()
                    else:
                        self.stdout.write(f"  • Partition Key: {self.style.WARNING(current_pk)}")
                
                indexing = container_props.get('indexing_policy')
                if indexing:
                    self.stdout.write(f"  • Indexing Mode: {self.style.WARNING(indexing)}")
            
            return True
        else:
            self.stdout.write(self.style.ERROR(f'❌ Connection failed: {status["error"]}'))
            return False

    def _setup_cosmosdb(self, force=False):
        """Setup CosmosDB database and container."""
        self.stdout.write(self.style.HTTP_INFO('\n🚀 Setting up CosmosDB...'))
        
        if force:
            self.stdout.write(
                self.style.WARNING('⚠️  Force mode: This will recreate the container and delete existing data!')
            )
            confirm = input('Type "yes" to continue: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('❌ Setup cancelled'))
                return
        
        success = initialize_cosmosdb()
        
        if success:
            self.stdout.write(self.style.SUCCESS('\n✅ CosmosDB setup completed successfully!'))
            self.stdout.write('')
            self.stdout.write(self.style.HTTP_INFO('📊 Container Configuration:'))
            self.stdout.write('  • Partition Key: /user_id (optimized for user queries)')
            self.stdout.write('  • Throughput: 400 RU/s (minimum cost)')
            self.stdout.write('  • Indexing: Optimized for task management queries')
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('🎉 Your application is ready to use CosmosDB!'))
        else:
            self.stdout.write(self.style.ERROR('\n❌ CosmosDB setup failed!'))
            self.stdout.write('Check the logs for more details.')

    def _display_setup_instructions(self):

        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('📋 Setup Instructions:'))
        self.stdout.write('')
        self.stdout.write('1. Copy your .env.example to .env:')
        self.stdout.write(f'   {self.style.WARNING("cp .env.example .env")}')
        self.stdout.write('')
        self.stdout.write('2. Configure your Azure CosmosDB credentials in .env:')
        self.stdout.write(f'   {self.style.WARNING("COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/")}')
        self.stdout.write(f'   {self.style.WARNING("COSMOS_KEY=your-cosmos-key-here")}')
        self.stdout.write(f'   {self.style.WARNING("COSMOS_DATABASE=tasks")}')
        self.stdout.write(f'   {self.style.WARNING("COSMOS_CONTAINER=tasks-manager")}')
        self.stdout.write('')
        self.stdout.write('3. Restart your application and run this command again.')

    def _display_partition_key_warning(self):

        self.stdout.write('')
        self.stdout.write(self.style.ERROR('⚠️  PARTITION KEY OPTIMIZATION WARNING'))
        self.stdout.write('')
        self.stdout.write('Current partition key "/id" is not optimal for a task management system.')
        self.stdout.write('Recommended: Use "/user_id" for better performance.')
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('Benefits of "/user_id" partition key:'))
        self.stdout.write('  • Queries filter by user (most common pattern)')
        self.stdout.write('  • Better data distribution across partitions')
        self.stdout.write('  • Avoids cross-partition queries')
        self.stdout.write('  • Lower RU consumption')
        self.stdout.write('  • Better scalability')
        self.stdout.write('')
        self.stdout.write('To migrate to the optimal partition key:')
        self.stdout.write('1. Export existing data')
        self.stdout.write('2. Delete and recreate container with --force')
        self.stdout.write('3. Re-import data with user_id field')
