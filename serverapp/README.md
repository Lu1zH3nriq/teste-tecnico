# Backend Django REST Framework para To-Do List

## Estrutura

Este diretório contém a API REST desenvolvida com Django REST Framework, configurada para usar Azure CosmosDB.

## Principais Componentes

- **todolist_project/**: Configurações principais do Django
- **core/**: Modelos base e configurações gerais
- **tasks/**: App para gerenciamento de tarefas
- **authentication/**: App para autenticação de usuários
- **requirements.txt**: Dependências Python
- **Dockerfile**: Configuração para containerização

## Configuração do CosmosDB

O projeto utiliza Azure CosmosDB com API SQL. As configurações estão em `settings.py` e utilizam variáveis de ambiente para segurança.

## API Endpoints

### Autenticação
- `POST /api/auth/register/` - Registro de usuário
- `POST /api/auth/login/` - Login de usuário
- `POST /api/auth/refresh/` - Renovar token

### Tarefas
- `GET /api/tasks/` - Listar tarefas
- `POST /api/tasks/` - Criar tarefa
- `GET /api/tasks/{id}/` - Detalhar tarefa
- `PUT /api/tasks/{id}/` - Atualizar tarefa
- `DELETE /api/tasks/{id}/` - Deletar tarefa
