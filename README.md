# To-Do List - Sistema de Gerenciamento de Tarefas

## Descrição do Projeto

Sistema completo de gerenciamento de tarefas com funcionalidades avançadas incluindo compartilhamento entre usuários, autenticação JWT e interface moderna. O projeto utiliza arquitetura desacoplada com API REST e frontend React.

### Funcionalidades Principais
-  Autenticação segura com JWT
-  CRUD completo de tarefas
-  Compartilhamento de tarefas entre usuários
-  Busca e filtros avançados
-  Interface responsiva
-  Suite completa de testes automatizados
-  Documentação automática da API
-  

## Executando com Docker

### Configuração Completa com Docker Compose

O projeto inclui configuração Docker para execução completa em containers:

#### Pré-requisitos
- Docker instalado e rodando
- Docker Compose instalado

#### Passos para execução:

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd teste-tecnico-GestaoOPME
```


2. **Execute com Docker Compose:**
```bash
# Build e start de todos os serviços
docker-compose up --build

# Em background (detached mode)
docker-compose up -d --build

# Apenas rebuild sem cache
docker-compose build --no-cache
docker-compose up
```

3. **Acesse os serviços:**
- **Frontend React**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Documentação Swagger**: http://localhost:8000/docs/swagger/
- **Admin Django**: http://localhost:8000/admin/

> **⚠️ Importante**: O frontend precisa acessar o backend via `localhost:8000`, não via nome do serviço Docker. Esta configuração já está definida no `docker-compose.yml` com `REACT_APP_API_URL=http://localhost:8000`.

#### Comandos Docker Úteis

```bash
# Ver logs dos containers
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f frontend
docker-compose logs -f backend

# Parar todos os serviços
docker-compose down

# Parar e remover volumes
docker-compose down -v

# Executar comandos no container do backend
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Executar testes no container
docker-compose exec backend python -m pytest Tests/test_api.py -v

# Rebuild apenas um serviço
docker-compose build frontend
docker-compose up frontend

# Script de teste automatizado (Windows PowerShell)
.\test-docker.ps1
```

### Estrutura do docker-compose.yml

```yaml
version: '3.8'
services:
  serverapp:          #  Backend Django
    build: ./serverapp
    ports:
      - "8000:8000"
    volumes:
      - ./serverapp:/app
    environment:
      - DEBUG=1
      
  webapp:             #  Frontend React
    build: ./webapp
    ports:
      - "3000:3000"
    volumes:
      - ./webapp:/app
    depends_on:
      - serverapp
```

## Arquitetura do Sistema

```
 teste-tecnico-GestaoOPME/
├──  serverapp/               # Backend - Django REST Framework
│   ├──  authentication/     # Sistema de autenticação
│   ├──  tasks/               # API de tarefas
│   ├──  core/                # Configurações e utilidades
│   ├──  Tests/               # Testes automatizados
│   ├──  manage.py            # CLI do Django
│   ├──  requirements.txt     # Dependências Python
│   └──  Dockerfile           # Container do backend
├──  webapp/                  # Frontend - React
│   ├──  src/                 # Código fonte React
│   │   ├──  components/      # Componentes reutilizáveis
│   │   ├──  pages/           # Páginas da aplicação
│   │   ├──  services/        # Serviços de API
│   │   └──  context/         # Context API
│   ├──  package.json         # Dependências Node.js
│   └──  Dockerfile           # Container do frontend
├──  docker-compose.yml       # Orquestração de containers
└──  README.md                # Documentação principal
```

##  Backend API (serverapp/)

### Estrutura da API Django REST Framework

O backend é construído com Django REST Framework seguindo padrões modernos de desenvolvimento:

```
serverapp/
├── authentication/             #  Sistema de Autenticação
│   ├── views.py               # Login, registro, refresh token
│   ├── serializers.py         # Validação de dados
│   ├── urls.py                # Rotas de auth
│   └── cosmos_models.py       # Integração Azure Cosmos DB
├── tasks/                     #  API de Tarefas
│   ├── models.py              # Modelo de dados Task
│   ├── views.py               # CRUD + compartilhamento
│   ├── serializers.py         # Validação e serialização
│   ├── urls.py                # Rotas de tarefas
│   └── migrations/            # Migrações do banco
├── core/                      #  Configurações Centrais
│   ├── models.py              # Modelos base
│   ├── cosmosdb.py            # Cliente Cosmos DB
│   └── cosmos_service.py      # Serviços Cosmos
├── Tests/                     #  Testes Automatizados
│   ├── test_api.py            # 46 testes da API
│   ├── pytest.ini            # Configuração pytest
│   └── README.md              # Documentação dos testes
├── todolist_project/          #  Configurações Django
│   ├── settings.py            # Configurações principais
│   ├── urls.py                # URLs principais
│   └── wsgi.py                # WSGI config
└── manage.py                  # CLI do Django
```

### Principais Endpoints da API

```
 Autenticação:
POST /api/auth/register/        # Registro de usuário
POST /api/auth/login/           # Login
POST /api/auth/token/refresh/   # Renovar token

 Tarefas:
GET    /api/tasks/              # Listar tarefas (próprias + compartilhadas)
POST   /api/tasks/              # Criar nova tarefa
GET    /api/tasks/{id}/         # Detalhes da tarefa
PUT    /api/tasks/{id}/         # Atualizar tarefa
DELETE /api/tasks/{id}/         # Deletar tarefa
PATCH  /api/tasks/{id}/toggle/  # Alternar status de conclusão

 Compartilhamento:
GET  /api/tasks/{id}/shared-users/    # Listar usuários compartilhados
POST /api/tasks/{id}/shared-users/    # Compartilhar com usuário
POST /api/tasks/{id}/remove-user/     # Remover compartilhamento

 Documentação:
GET /api/docs/swagger/          # Interface Swagger
GET /api/docs/redoc/            # Interface ReDoc
```

### Como Executar o Backend Localmente

#### Pré-requisitos
- Python 3.8+ instalado
- pip (gerenciador de pacotes Python)

#### Passos para execução:

1. **Navegue para o diretório do backend:**
```bash
cd serverapp/
```

2. **Crie e ative um ambiente virtual:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```


5. **Execute as migrações do banco:**
```bash
python manage.py migrate
```

6. **Inicie o servidor de desenvolvimento:**
```bash
python manage.py runserver
```

7. **Acesse a API:**
- API Base: http://localhost:8000/api/
- Documentação Swagger: http://localhost:8000/api/docs/swagger/
- Admin Django: http://localhost:8000/admin/

#### Executar Testes do Backend
```bash
# Executar todos os testes
python -m pytest Tests/test_api.py -v

# Executar testes específicos
python -m pytest Tests/test_api.py::TestAuthenticationAPI -v

# Executar com cobertura
pytest Tests/test_api.py --cov=tasks --cov=authentication
```

## Frontend React (webapp/)

### Estrutura do Frontend React

O frontend é construído com React moderno utilizando hooks e Context API:

```
webapp/
├── public/                    #  Arquivos públicos
│   ├── index.html            # Template HTML principal
│   └── manifest.json         # PWA manifest
├── src/                      #  Código fonte React
│   ├── components/           #  Componentes reutilizáveis
│   │   ├── auth/            # Componentes de autenticação
│   │   │   ├── LoginForm.js
│   │   │   └── RegisterForm.js
│   │   └── common/          # Componentes comuns
│   │       ├── Header.js
│   │       ├── DataTable.js
│   │       ├── ConfirmModal.js
│   │       ├── ErrorModal.js
│   │       └── ShareTaskModal.js
│   ├── pages/               #  Páginas da aplicação
│   │   ├── Login/           # Página de login
│   │   ├── Register/        # Página de registro
│   │   └── ToDoList/        # Página principal de tarefas
│   ├── services/            #  Serviços de API
│   │   ├── api.js           # Cliente HTTP configurado
│   │   └── authService.js   # Serviços de autenticação
│   ├── context/             #  Context API
│   │   └── AuthContext.js   # Contexto de autenticação
│   ├── App.js               # Componente principal
│   ├── App.css              # Estilos globais
│   ├── index.js             # Ponto de entrada
│   └── index.css            # Estilos base
├── package.json             #  Dependências e scripts
└── Dockerfile               #  Container configuration
```

### Principais Funcionalidades do Frontend

####  Sistema de Autenticação
- Login/Registro com validação de formulários
- Gerenciamento automático de tokens JWT
- Redirecionamento baseado em autenticação
- Logout seguro com limpeza de estado

####  Gerenciamento de Tarefas
- Interface intuitiva para CRUD de tarefas
- Filtros por status, prioridade e busca textual
- Ordenação customizável
- Paginação de resultados

####  Compartilhamento
- Modal para compartilhar tarefas por email
- Visualização de usuários com acesso
- Remoção de compartilhamentos
- Indicadores visuais de propriedade

####  Interface Moderna
- Design responsivo para mobile e desktop
- Modais de confirmação para ações críticas
- Feedback visual para ações do usuário
- Tratamento de erros com mensagens específicas

### Como Executar o Frontend Localmente

#### Pré-requisitos
- Node.js 16+ instalado
- npm ou yarn (gerenciador de pacotes)

#### Passos para execução:

1. **Navegue para o diretório do frontend:**
```bash
cd webapp/
```

2. **Instale as dependências:**
```bash
npm install
# ou
yarn install
```

3. **Configure variáveis de ambiente**
```bash
# Crie um arquivo .env na raiz do webapp/
REACT_APP_API_URL=http://localhost:8000/api
```

4. **Inicie o servidor de desenvolvimento:**
```bash
npm start
# ou
yarn start
```

5. **Acesse a aplicação:**
- Frontend: http://localhost:3000
- A aplicação abrirá automaticamente no navegador

#### Scripts Disponíveis
```bash
npm start          # Inicia servidor de desenvolvimento
npm run build      # Gera build de produção
npm test           # Executa testes (se configurados)
npm run eject      # Ejeta configuração do Create React App
```

##  Banco de Dados

### SQLite (Desenvolvimento)
- Banco principal para tarefas e relações
- Arquivo: `serverapp/db.sqlite3`
- Migrações automáticas do Django


##  Tecnologias Utilizadas

### Backend
- **Django 4.2.7** - Framework web Python
- **Django REST Framework 3.14.0** - API REST
- **drf-yasg 1.21.10** - Documentação Swagger/OpenAPI
- **django-cors-headers** - CORS para frontend
- **PyJWT** - Autenticação JWT
- **pytest-django** - Testes automatizados

### Frontend
- **React 18+** - Biblioteca JavaScript
- **Axios** - Cliente HTTP
- **React Router** - Navegação SPA
- **CSS3** - Estilização moderna

### DevOps & Infraestrutura
- **Docker** - Containerização
- **Docker Compose** - Orquestração
- **SQLite** - Banco de dados local

## Contato

**Desenvolvedor**: Luiz Henrique  
**Email**: [lh.m21112000@gmail.com]  
**GitHub**: [@Lu1zH3nriq](https://github.com/Lu1zH3nriq)

---

**Última atualização**: Agosto 2025  
**Versão**: 1.0.0

