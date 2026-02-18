# Backend — Unicamp VestIA

API backend em FastAPI para o chatbot Unicamp VestIA, com pipeline RAG (Retrieval-Augmented Generation) para fornecer respostas fundamentadas sobre o Vestibular Unicamp 2026. Desenvolvido a partir da base do [Desafio Estágio Verão 2026 da NeuralMind](https://github.com/neuralmind-ai/desafio-nm-estagio-de-verao-2026).

## Funcionalidades Desenvolvidas

- **Pipeline RAG completo**
  - Web scraping assíncrono de páginas HTML e PDFs com crawling de URLs
  - Ingestão de documentos no Chroma DB com embeddings OpenAI (`text-embedding-3-small`)
  - Busca por similaridade (K=7 documentos por query)
  - Reescrita de queries com 4 estratégias: expansão, simplificação, reformulação e combinada
  - Ingestão automática opcional na inicialização do servidor
  - Construção de contexto com citação de fontes
- **Streaming de respostas** — Respostas em tempo real via Server-Sent Events (SSE)
- **Persistência de conversas** — CRUD completo de chats e mensagens em PostgreSQL
- **Geração automática de títulos** — Títulos descritivos gerados por IA para cada conversa
- **Autenticação GitHub OAuth 2.0** — Fluxo OAuth completo com tokens JWT (HS256, 60min) e cookies seguros
- **Geração de relatórios** — Endpoint `/report` para exportação em PDF
- **Health checks** — Monitoramento da disponibilidade do serviço

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
