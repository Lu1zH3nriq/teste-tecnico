
#!/bin/bash

echo "🚀 Iniciando aplicação Django..."

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: manage.py não encontrado. Verificando diretório..."
    ls -la
    exit 1
fi

echo "📋 Verificando estrutura do projeto..."
python -c "
import sys
import os
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todolist_project.settings')

try:
    import django
    django.setup()
    print('✅ Django configurado com sucesso')
except Exception as e:
    print(f'❌ Erro na configuração do Django: {e}')
    sys.exit(1)
"

sleep 2

echo "📦 Aplicando migrações do banco de dados..."
python manage.py migrate

echo "📂 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "👤 Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superusuário criado: admin/admin123')
else:
    print('✅ Superusuário já existe')
"

echo "🌐 Iniciando servidor Django na porta 8000..."
python manage.py runserver 0.0.0.0:8000
