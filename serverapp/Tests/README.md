# Tests - Sistema de Gerenciamento de Tarefas

Este diretório contém todos os testes automatizados para a API do sistema de gerenciamento de tarefas. Os testes são escritos usando pytest e cobrem todas as funcionalidades principais da aplicação.

## Estrutura dos Testes

### Arquivos de Teste

- **`test_api.py`** - Testes principais da API REST
- **`pytest.ini`** - Configurações do pytest
- **`conftest.py`** - Configurações e fixtures compartilhadas (se existir)

## Classes de Teste e Funcionalidades

### 1. TestAuthenticationAPI
**Propósito**: Testa o sistema de autenticação de usuários

**Testes incluídos**:
- `test_register_user_success` - Valida registro de novo usuário com dados válidos
- `test_register_user_invalid_data` - Testa registro com dados inválidos (email malformado, senhas diferentes)
- `test_register_duplicate_email` - Verifica rejeição de emails já cadastrados
- `test_login_success` - Testa login com credenciais corretas
- `test_login_invalid_credentials` - Valida rejeição de credenciais incorretas
- `test_login_nonexistent_user` - Testa login com usuário inexistente
- `test_refresh_token` - Valida renovação de tokens JWT

### 2. TestTasksAPI
**Propósito**: Testa operações CRUD básicas de tarefas

**Testes incluídos**:
- `test_create_task_success` - Criação de tarefa com todos os dados
- `test_create_task_minimal_data` - Criação com dados mínimos (apenas título)
- `test_create_task_invalid_data` - Validação de dados inválidos
- `test_create_task_unauthorized` - Rejeição de criação sem autenticação
- `test_list_tasks_includes_owned_and_shared` - Listagem inclui tarefas próprias e compartilhadas
- `test_list_tasks_with_filters` - Filtros por status, prioridade, etc.
- `test_list_tasks_with_search` - Busca textual em título e descrição
- `test_get_task_detail_own_task` - Detalhes de tarefa própria
- `test_get_task_detail_shared_task` - Detalhes de tarefa compartilhada
- `test_get_task_not_found` - Erro 404 para tarefas inexistentes
- `test_update_own_task` - Atualização de tarefa própria
- `test_update_shared_task_forbidden` - Proibição de atualizar tarefa compartilhada
- `test_delete_own_task` - Exclusão de tarefa própria
- `test_delete_shared_task_forbidden` - Proibição de excluir tarefa compartilhada

### 3. TestTaskToggleComplete
**Propósito**: Testa funcionalidade de alternar status de conclusão

**Testes incluídos**:
- `test_toggle_complete_own_task` - Marcar tarefa própria como concluída
- `test_toggle_uncomplete_own_task` - Desmarcar tarefa própria como pendente
- `test_toggle_complete_shared_task_forbidden` - Proibição de alterar status de tarefa compartilhada

### 4. TestTaskSharingAPI
**Propósito**: Testa sistema de compartilhamento de tarefas entre usuários

**Testes incluídos**:
- `test_get_shared_users_empty` - Lista vazia de usuários compartilhados
- `test_get_shared_users_with_sharing` - Lista com usuários compartilhados
- `test_get_shared_users_as_shared_user` - Visualização como usuário compartilhado
- `test_share_task_with_user` - Compartilhar tarefa com usuário válido
- `test_share_task_with_nonexistent_user` - Erro ao compartilhar com usuário inexistente
- `test_share_task_with_owner` - Proibição de compartilhar com próprio dono
- `test_share_task_already_shared` - Erro ao compartilhar novamente com mesmo usuário
- `test_share_task_not_owner` - Proibição de compartilhar tarefa alheia
- `test_remove_user_from_share` - Remover usuário do compartilhamento
- `test_remove_user_not_shared` - Erro ao remover usuário não compartilhado

### 5. TestValidationAPI
**Propósito**: Testa validações de dados de entrada

**Testes incluídos**:
- `test_title_required` - Título é campo obrigatório
- `test_invalid_priority` - Rejeição de prioridades inválidas
- `test_invalid_status` - Rejeição de status inválidos
- `test_valid_due_date_format` - Aceitação de formato de data válido
- `test_invalid_due_date_format` - Rejeição de formato de data inválido

### 6. TestTaskOrdering
**Propósito**: Testa ordenação de tarefas

**Testes incluídos**:
- `test_ordering_by_created_at` - Ordenação por data de criação (crescente/decrescente)
- `test_ordering_by_priority` - Ordenação por prioridade

### 7. TestPagination
**Propósito**: Testa paginação de resultados

**Testes incluídos**:
- `test_pagination_structure` - Estrutura correta da resposta paginada
- `test_pagination_navigation` - Navegação entre páginas

### 8. TestTaskModelMethods
**Propósito**: Testa métodos específicos do modelo Task

**Testes incluídos**:
- `test_share_with_user` - Método de compartilhamento no modelo
- `test_unshare_with_user` - Método de remoção de compartilhamento
- `test_get_all_users_with_access` - Lista todos usuários com acesso
- `test_is_overdue_property` - Propriedade para verificar tarefas vencidas
- `test_get_tags_list` - Método para obter lista de tags

## Como Executar os Testes

### Pré-requisitos
1. Python 3.8+ instalado
2. Dependências instaladas:
```bash
pip install -r requirements.txt
```

### Comandos de Execução

#### Executar todos os testes
```bash
# A partir do diretório serverapp/
python -m pytest Tests/test_api.py -v

# Ou usando pytest diretamente
pytest Tests/test_api.py -v
```

#### Executar testes específicos

**Por classe de teste:**
```bash
python -m pytest Tests/test_api.py::TestAuthenticationAPI -v
python -m pytest Tests/test_api.py::TestTasksAPI -v
python -m pytest Tests/test_api.py::TestTaskSharingAPI -v
```

**Por teste individual:**
```bash
python -m pytest Tests/test_api.py::TestAuthenticationAPI::test_login_success -v
python -m pytest Tests/test_api.py::TestTasksAPI::test_create_task_success -v
```

## Dependências
- pytest
- pytest-django
- Django REST Framework
- djangorestframework-simplejwt

## Observações
- Os testes utilizam banco de dados em memória
- Emails únicos são gerados automaticamente para evitar conflitos
- Cada teste é independente e pode ser executado isoladamente
- Os testes cobrem todos os endpoints da API
- Validações de segurança e autenticação são rigorosamente testadas
