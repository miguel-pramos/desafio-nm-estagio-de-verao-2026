# Unicamp VestIA — Chatbot com RAG para o Vestibular Unicamp 2026

Projeto desenvolvido por **Miguel Ramos** como parte do processo seletivo do [Desafio Estágio Verão 2026 da NeuralMind](https://github.com/neuralmind-ai/desafio-nm-estagio-de-verao-2026).

O desafio consistia em construir funcionalidades sobre uma **aplicação base** fornecida pela NeuralMind — um chatbot full-stack com FastAPI, Next.js, PostgreSQL, autenticação via GitHub OAuth e streaming de respostas. A partir dessa base, desenvolvi um **pipeline RAG completo** e diversas melhorias de UX e gestão de conversas, descritas abaixo.

## O que já vinha na base

A aplicação base fornecida pelo desafio incluía:

- Chat com streaming de respostas via SSE (Server-Sent Events)
- Autenticação via GitHub OAuth 2.0 com JWT
- Persistência de chats e mensagens em PostgreSQL (SQLModel + Alembic)
- Interface Next.js com Tailwind CSS, shadcn/ui e tema claro/escuro
- Deploy via Docker Compose
- Health checks

## Funcionalidades que eu desenvolvi

As seguintes funcionalidades foram implementadas por mim sobre a base fornecida:

### Pipeline RAG (Retrieval-Augmented Generation)
- **Web scraper** — Scraping assíncrono de páginas HTML com crawling recursivo de URLs
- **Scraping de PDFs** — Extração de conteúdo de documentos PDF
- **Embeddings** — Geração de embeddings com OpenAI (`text-embedding-3-small`) e armazenamento no Chroma DB
- **Construção de contexto** — Montagem de contexto a partir dos documentos recuperados, com citação de fontes
- **Integração RAG** — Integração do pipeline de retrieval no fluxo de chat existente
- **Reescrita de queries** — 4 estratégias de reescrita (expansão, simplificação, reformulação e combinada) para melhorar a recuperação de documentos

### Gestão de Conversas
- **Endpoint de chats existentes** — API para listar todas as conversas do usuário
- **Sidebar com histórico** — Exibição de todas as conversas na sidebar do frontend
- **Exclusão de chats** — Funcionalidade para apagar conversas
- **Geração automática de títulos** — Títulos descritivos gerados por IA para cada conversa (backend + exibição no frontend)

### Outros
- **Geração de relatórios** — Endpoint público para exportação de relatórios em PDF
- **Modularização** — Refatoração e organização do código em serviços, repositórios e utilitários

## Stack

| Camada     | Tecnologias                                                                                       |
| ---------- | ------------------------------------------------------------------------------------------------- |
| **Backend**  | Python, FastAPI, OpenAI SDK, LangChain, Chroma, SQLModel, Alembic, Authlib                      |
| **Frontend** | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Radix UI, AI SDK, React Markdown   |
| **Infra**    | PostgreSQL, Docker & Docker Compose                                                              |

## Pré-requisitos

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- [VS Code](https://code.visualstudio.com/) (recomendado — o projeto inclui um arquivo `project.code-workspace`)

Para desenvolvimento local sem Docker, consulte os READMEs de cada módulo para pré-requisitos específicos (Python 3.13+, Node.js 20+, etc.).

## Início Rápido

1. Clone o repositório:
   ```bash
   git clone https://github.com/miguel-pramos/desafio-nm-estagio-de-verao-2026.git
   ```
2. Configure as variáveis de ambiente nos arquivos `.env` do backend e frontend (veja os READMEs de cada pasta para detalhes).
3. Suba todos os serviços com Docker Compose:
   ```bash
   docker compose up --build
   ```
4. Acesse a aplicação em `http://localhost:3000` e a documentação da API em `http://localhost:8000/docs`.

Para desenvolvimento local sem Docker, consulte o [README do backend](backend/README.md) e o [README do frontend](frontend/README.md).

## Estrutura de Pastas

```
desafio-nm-estagio-de-verao-2026/
├── backend/                     # API FastAPI + pipeline RAG
├── frontend/                    # Aplicação Next.js
├── docs/                        # Assets de documentação (capturas de tela)
├── docker-compose.yml           # Orquestra todos os serviços
├── project.code-workspace       # Configuração da VS Code Workspace
└── README.md                    # Este arquivo
```

## Capturas de Tela

![Tela de login](docs/assets/sign-in.png)
![Tela de overview](docs/assets/overview.png)
![Tela de chat](docs/assets/chatting.png)

## Documentação

- [Backend README](backend/README.md) — Detalhes da API, pipeline RAG e comandos de desenvolvimento.
- [Frontend README](frontend/README.md) — Detalhes da interface, componentes e comandos de desenvolvimento.

## Autor

**Miguel Ramos** — [GitHub](https://github.com/miguel-pramos)

Projeto desenvolvido como parte do processo seletivo do [Desafio Estágio Verão 2026 da NeuralMind](https://github.com/neuralmind-ai/desafio-nm-estagio-de-verao-2026). A aplicação base (chat com streaming, autenticação OAuth, persistência e interface) foi fornecida pela NeuralMind; as funcionalidades de RAG, gestão de conversas e demais melhorias foram desenvolvidas por mim.

---

[Licença](LICENSE) | [Política de Segurança](SECURITY.md)
