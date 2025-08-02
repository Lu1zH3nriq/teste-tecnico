# Testes do Projeto TodoList

Esta pasta contém todos os arquivos relacionados aos testes do projeto.

## Arquivos incluídos

### Testes principais
- **test_api.py**: Suite completa de testes da API com 31 testes cobrindo:
  - Autenticação (registro, login, refresh token)
  - CRUD de tarefas
  - Validações
  - Permissões
  - Paginação e ordenação

### Configuração
- **conftest.py**: Configuração do pytest para Django
- **pytest.ini**: Configurações do pytest
- **__init__.py**: Marca a pasta como um pacote Python

### Utilitários de teste
- **create_random_tasks.py**: Script para criar tarefas aleatórias para testes
- **create_random_tasks_with_login.py**: Script para criar tarefas via API com login

## Detalhamento dos 31 Testes

### 🔐 TestAuthenticationAPI (7 testes)

1. **test_register_user_success**
   - **O que faz**: Testa registro de usuário com dados válidos
   - **Verifica**: Criação de conta, geração de tokens JWT, salvamento no banco
   - **Endpoint**: `POST /api/auth/register/`

2. **test_register_user_invalid_data**
   - **O que faz**: Testa registro com dados inválidos (email malformado, senhas diferentes)
   - **Verifica**: Validação de entrada e retorno de erros apropriados
   - **Endpoint**: `POST /api/auth/register/`

3. **test_register_duplicate_email**
   - **O que faz**: Testa tentativa de registro com email já existente
   - **Verifica**: Prevenção de emails duplicados e erro apropriado
   - **Endpoint**: `POST /api/auth/register/`

4. **test_login_success**
   - **O que faz**: Testa login com credenciais válidas
   - **Verifica**: Autenticação bem-sucedida e geração de tokens
   - **Endpoint**: `POST /api/auth/login/`

5. **test_login_invalid_credentials**
   - **O que faz**: Testa login com senha incorreta
   - **Verifica**: Rejeição de credenciais inválidas
   - **Endpoint**: `POST /api/auth/login/`

6. **test_login_nonexistent_user**
   - **O que faz**: Testa login com email não cadastrado
   - **Verifica**: Tratamento de usuário inexistente
   - **Endpoint**: `POST /api/auth/login/`

7. **test_refresh_token**
   - **O que faz**: Testa renovação de token de acesso usando refresh token
   - **Verifica**: Funcionamento do mecanismo de renovação JWT
   - **Endpoint**: `POST /api/auth/token/refresh/`

### 📝 TestTasksAPI (11 testes)

8. **test_create_task_success**
   - **O que faz**: Testa criação de tarefa com dados completos
   - **Verifica**: Criação bem-sucedida com todos os campos preenchidos
   - **Endpoint**: `POST /api/tasks/`

9. **test_create_task_minimal_data**
   - **O que faz**: Testa criação de tarefa apenas com título (dados mínimos)
   - **Verifica**: Criação com campos obrigatórios apenas
   - **Endpoint**: `POST /api/tasks/`

10. **test_create_task_invalid_data**
    - **O que faz**: Testa criação com dados inválidos
    - **Verifica**: Validação de entrada e rejeição de dados incorretos
    - **Endpoint**: `POST /api/tasks/`

11. **test_create_task_unauthorized**
    - **O que faz**: Testa criação de tarefa sem autenticação
    - **Verifica**: Proteção de endpoint com autenticação obrigatória
    - **Endpoint**: `POST /api/tasks/`

12. **test_list_tasks**
    - **O que faz**: Testa listagem de tarefas do usuário autenticado
    - **Verifica**: Retorno correto das tarefas com paginação
    - **Endpoint**: `GET /api/tasks/`

13. **test_list_tasks_with_filters**
    - **O que faz**: Testa filtros por status e prioridade
    - **Verifica**: Funcionamento dos query parameters de filtro
    - **Endpoint**: `GET /api/tasks/?status=pending&priority=high`

14. **test_list_tasks_with_search**
    - **O que faz**: Testa busca por texto no título e descrição
    - **Verifica**: Funcionalidade de pesquisa textual
    - **Endpoint**: `GET /api/tasks/?search=termo`

15. **test_get_task_detail**
    - **O que faz**: Testa visualização de detalhes de uma tarefa específica
    - **Verifica**: Retorno completo dos dados da tarefa
    - **Endpoint**: `GET /api/tasks/{id}/`

16. **test_get_task_not_found**
    - **O que faz**: Testa acesso a tarefa inexistente
    - **Verifica**: Retorno de erro 404 para ID inválido
    - **Endpoint**: `GET /api/tasks/99999/`

17. **test_update_task**
    - **O que faz**: Testa atualização completa de uma tarefa (PUT)
    - **Verifica**: Modificação de todos os campos da tarefa
    - **Endpoint**: `PUT /api/tasks/{id}/`

18. **test_partial_update_task**
    - **O que faz**: Testa atualização parcial de uma tarefa (PATCH)
    - **Verifica**: Modificação de campos específicos
    - **Endpoint**: `PATCH /api/tasks/{id}/`

19. **test_toggle_task_completion**
    - **O que faz**: Testa marcação/desmarcação de tarefa como concluída
    - **Verifica**: Alternância do status de conclusão
    - **Endpoint**: `PATCH /api/tasks/{id}/toggle/`

20. **test_delete_task**
    - **O que faz**: Testa exclusão de uma tarefa
    - **Verifica**: Remoção definitiva da tarefa
    - **Endpoint**: `DELETE /api/tasks/{id}/`

21. **test_access_other_user_task**
    - **O que faz**: Testa tentativa de acesso à tarefa de outro usuário
    - **Verifica**: Isolamento de dados entre usuários
    - **Endpoint**: `GET /api/tasks/{id_outro_usuario}/`

### 🔒 TestTaskPermissions (1 teste)

22. **test_user_can_only_see_own_tasks**
    - **O que faz**: Testa que usuário só vê suas próprias tarefas na listagem
    - **Verifica**: Isolamento completo de dados entre diferentes usuários
    - **Endpoint**: `GET /api/tasks/`

### ✅ TestTaskValidation (6 testes)

23. **test_task_title_required**
    - **O que faz**: Testa que o título é campo obrigatório
    - **Verifica**: Validação de campo obrigatório
    - **Endpoint**: `POST /api/tasks/`

24. **test_invalid_priority**
    - **O que faz**: Testa prioridade inválida (fora de low/medium/high)
    - **Verifica**: Validação de enum de prioridade
    - **Endpoint**: `POST /api/tasks/`

25. **test_invalid_status**
    - **O que faz**: Testa status inválido (fora de pending/in_progress/completed)
    - **Verifica**: Validação de enum de status
    - **Endpoint**: `POST /api/tasks/`

26. **test_valid_due_date_format**
    - **O que faz**: Testa formato válido de data de vencimento
    - **Verifica**: Aceitação de formato ISO 8601
    - **Endpoint**: `POST /api/tasks/`

27. **test_invalid_due_date_format**
    - **O que faz**: Testa formato inválido de data
    - **Verifica**: Rejeição de formatos de data incorretos
    - **Endpoint**: `POST /api/tasks/`

### 📊 TestTaskOrdering (2 testes)

28. **test_ordering_by_created_at**
    - **O que faz**: Testa ordenação das tarefas por data de criação
    - **Verifica**: Ordenação cronológica (mais recentes primeiro)
    - **Endpoint**: `GET /api/tasks/?ordering=-created_at`

29. **test_ordering_by_priority**
    - **O que faz**: Testa ordenação por prioridade (high > medium > low)
    - **Verifica**: Ordenação por importância
    - **Endpoint**: `GET /api/tasks/?ordering=priority`

### 📄 TestPagination (2 testes)

30. **test_pagination_structure**
    - **O que faz**: Testa estrutura da resposta paginada
    - **Verifica**: Presença de count, next, previous, results
    - **Endpoint**: `GET /api/tasks/`

31. **test_pagination_navigation**
    - **O que faz**: Testa navegação entre páginas (próxima/anterior)
    - **Verifica**: Links de navegação e contagem correta
    - **Endpoint**: `GET /api/tasks/?page=2`

## Como executar os testes

### Todos os testes
```bash
cd Tests
python -m pytest test_api.py -v
```

### Teste específico
```bash
cd Tests
python -m pytest test_api.py::TestAuthenticationAPI::test_login_success -v
```

## Resultados esperados
✅ **31 testes devem passar com sucesso**

### Cobertura por categoria
- 🔐 **7 testes de autenticação** - Registro, login, tokens
- 📝 **11 testes de CRUD de tarefas** - Criar, ler, atualizar, deletar
- 🔒 **1 teste de permissões** - Isolamento entre usuários
- ✅ **6 testes de validação** - Campos obrigatórios e formatos
- 📊 **2 testes de ordenação** - Por data e prioridade
- 📄 **2 testes de paginação** - Estrutura e navegação

## Dependências
- pytest
- pytest-django
- Django REST Framework
- djangorestframework-simplejwt

## Observações
- Os testes utilizam banco de dados em memória
- Cosmos DB é testado quando configurado
- Emails únicos são gerados automaticamente para evitar conflitos
- Cada teste é independente e pode ser executado isoladamente
- Os testes cobrem todos os endpoints da API
- Validações de segurança e autenticação são rigorosamente testadas
