# Fast Zero

Fast Zero é uma API RESTful desenvolvida com FastAPI para gerenciamento de usuários, autenticação e tarefas (todos). O projeto utiliza SQLAlchemy para ORM, autenticação JWT, e segue boas práticas de organização de código.

## Requisitos

- Python 3.12
- [Poetry](https://python-poetry.org/) para gerenciamento de dependências

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/fast_zero.git
cd fast_zero
```

2. Instale as dependências:

```bash
poetry install
```

3. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
DATABASE_URL="sqlite:///seu_banco.db"
DATABASE_TEST_URL="sqlite:///:memory:"
SECRET_KEY="your_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Como rodar

1. Ative o ambiente virtual do Poetry:

```bash
poetry shell
```

2. Execute a aplicação:

```bash
task run
```

A API estará disponível em http://localhost:8000.

3. Para rodar os testes:

```bash
task test
```

## Endpoints Disponíveis

Autenticação

- POST /auth/token (Gera um token JWT para autenticação)
- GET /auth/refresh_token

Usuários

- POST /users/
- GET /users/
- PUT /users/{user_id}
- DELETE /users/{user_id}

Todos

- POST /todos/
- GET /todos/
- PUT /todos/{todo_id}
- DELETE /todos/{todo_id}
