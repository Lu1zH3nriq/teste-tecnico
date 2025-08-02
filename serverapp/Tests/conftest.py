import os
import django


def pytest_configure(config):
    """Configuração do pytest para Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todolist_project.settings')
    django.setup()
