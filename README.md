# To-Do List - Gerenciamento de Tarefas

## Descrição do Projeto

Aplicação web de gerenciamento de tarefas (To-Do List) com funcionalidades avançadas, desenvolvida utilizando:

- **Frontend**: React
- **Backend**: Django REST Framework 
- **Banco de Dados**: SQLite (local) + Azure Cosmos DB (usuários)
- **Containerização**: Docker e Docker Compose

## Arquitetura

```
├── serverapp/          # Backend Django REST Framework
├── webapp/             # Frontend React
├── docker-compose.yml  # Configuração dos contêineres
└── README.md          # Documentação
```

### Backend (serverapp)
- Django REST Framework para API REST
- Arquitetura híbrida: SQLite para tarefas + Azure Cosmos DB para usuários
- Autenticação JWT com integração Cosmos DB
- Swagger/OpenAPI documentação em `/docs/swagger/`
- Endpoints para CRUD completo de tarefas e usuários

### Frontend (webapp)
- React com hooks modernos
- Interface responsiva
- Comunicação com API via Axios
- Estado global para gerenciamento de tarefas

### Banco de Dados
- **SQLite**: Tarefas e dados locais (desenvolvimento)
- **Azure Cosmos DB**: Usuários em container específico
  - Database: `tasks`
  - Container: `users`
  - Partition Key: `/id`

## Tecnologias Utilizadas

### Backend
- Django 4.2.7
- Django REST Framework 3.14.0
- drf-yasg 1.21.10 (Swagger/OpenAPI)
- django-cors-headers
- PyJWT para autenticação
- azure-cosmos 4.5.1 para integração com Cosmos DB
- azure-identity 1.23.1 para autenticação Azure

### Frontend
- React 18+
- Axios para requisições HTTP
- React Router para navegação
- CSS Modules ou Styled Components

### DevOps
- Docker
- Docker Compose
- Azure CosmosDB

## Como Executar o Projeto

### Pré-requisitos
- Docker e Docker Compose instalados
- Conta Azure com CosmosDB configurado
- Node.js 18+ (para desenvolvimento local)
- Python 3.11+ (para desenvolvimento local)

### Configuração

1. Clone o repositório:
```bash
git clone <repository-url>
cd GESTAO-OPME-LTDA---Processo-Seletivo---Desenvolvedor-Python-J-nior
```

2. Configure as variáveis de ambiente para CosmosDB:
```bash
# Copie o arquivo .env.example para .env
cp .env.example .env

# Configure suas credenciais do CosmosDB no arquivo .env
```

3. Execute com Docker Compose:
```bash
docker-compose up --build
```

4. Acesse a aplicação:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentação da API: http://localhost:8000/api/docs/

## Estrutura do Projeto

### Pastas Principais
- `serverapp/`: Contém toda a aplicação Django
- `webapp/`: Contém toda a aplicação React

