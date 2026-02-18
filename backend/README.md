# Backend — Unicamp VestIA

API backend em FastAPI para o chatbot Unicamp VestIA. Desenvolvido como parte do processo seletivo do [Desafio Estágio Verão 2026 da NeuralMind](https://github.com/neuralmind-ai/desafio-nm-estagio-de-verao-2026).

A base fornecida pela NeuralMind já incluía a estrutura FastAPI, autenticação GitHub OAuth, streaming de respostas via SSE, persistência em PostgreSQL e health checks. As funcionalidades listadas abaixo foram desenvolvidas por mim sobre essa base.

## Funcionalidades que eu desenvolvi

### Pipeline RAG (Retrieval-Augmented Generation)
- **Web scraper** — Scraping assíncrono de páginas HTML com crawling recursivo de URLs
- **Scraping de PDFs** — Extração de conteúdo de documentos PDF
- **Embeddings** — Geração de embeddings com OpenAI (`text-embedding-3-small`) e armazenamento no Chroma DB
- **Construção de contexto** — Montagem de contexto a partir dos documentos recuperados, com citação de fontes
- **Integração RAG** — Integração do pipeline de retrieval no fluxo de chat existente
- **Reescrita de queries** — 4 estratégias de reescrita (expansão, simplificação, reformulação e combinada) para melhorar a recuperação de documentos

### Gestão de Conversas
- **Endpoint de chats existentes** — API para listar todas as conversas do usuário
- **Exclusão de chats** — Endpoint para apagar conversas
- **Geração automática de títulos** — Títulos descritivos gerados por IA para cada conversa

### Outros
- **Geração de relatórios** — Endpoint público `/report` para exportação em PDF
- **Modularização** — Refatoração do código em serviços, repositórios e utilitários

## Stack

- [**Python 3.13+**](https://www.python.org/) com [**uv**](https://github.com/astral-sh/uv), [**Ruff**](https://docs.astral.sh/ruff/) e [**Makefile**](https://www.gnu.org/software/make/)
- [**FastAPI**](https://fastapi.tiangolo.com/) — Framework web
- [**OpenAI Python SDK**](https://platform.openai.com/docs/api-reference/introduction?lang=python) — Integração com LLM
- [**LangChain**](https://python.langchain.com/) + [**Chroma**](https://www.trychroma.com/) — Pipeline RAG e vector store
- [**SQLModel**](https://sqlmodel.tiangolo.com/) + [**PostgreSQL**](https://www.postgresql.org/) — ORM e banco de dados
- [**Alembic**](https://alembic.sqlalchemy.org/) — Migrações de banco de dados
- [**Authlib**](https://docs.authlib.org/) — Autenticação OAuth
- [**Docker**](https://www.docker.com/) & [**Docker Compose**](https://docs.docker.com/compose/) — Conteinerização

## Pré-requisitos

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) gerenciador de pacotes
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) (para o banco de dados)

## Início Rápido

1. **Instale as dependências:**
     ```bash
     make install
     ```

2. **Configure o ambiente:**
     ```bash
     make setup-env
     ```
     Preencha os valores no arquivo `.env` gerado. Leia o conteúdo do arquivo para mais informações.

3. **Suba o container Docker do banco de dados:**
     ```bash
     make up-db
     ```

4. **Aplique as migrações do banco de dados:**
     ```bash
     make db-migrate
     ```

5. **Inicie o servidor de desenvolvimento:**
     ```bash
     make dev
     ```

A API estará disponível em `http://localhost:8000` com documentação interativa em `http://localhost:8000/docs`.

## Estrutura de Pastas

```
backend/
├── app/
│   ├── config/           # Configurações (IA, auth, DB, variáveis de ambiente)
│   ├── models/           # Modelos SQLModel (User, Chat, Message)
│   ├── repositories/     # Camada de acesso a dados (CRUD)
│   ├── routers/          # Endpoints da API (auth, chat, health, report)
│   ├── schemas/          # Schemas Pydantic (validação de entrada/saída)
│   ├── utils/            # Utilitários (JWT, streaming, conversão de mensagens)
│   └── main.py           # Ponto de entrada da aplicação
├── migrations/           # Migrações Alembic
├── tests/                # Testes automatizados
├── alembic.ini           # Configuração do Alembic
├── docker-compose.yml    # Serviços Docker (PostgreSQL)
└── Dockerfile            # Imagem Docker do backend
```

## Documentação

A documentação interativa da API é gerada automaticamente pelo FastAPI e está disponível em `http://localhost:8000/docs`.

Os principais comandos de desenvolvimento estão no `Makefile`. Execute `make help` para ver a lista completa.
