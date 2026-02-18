# Unicamp VestIA — Chatbot com RAG para o Vestibular Unicamp 2026

Aplicação full-stack de chatbot com inteligência artificial e **Retrieval-Augmented Generation (RAG)** que fornece respostas fundamentadas sobre o Vestibular Unicamp 2026. Desenvolvido como projeto para o [Desafio Estágio Verão 2026 da NeuralMind](https://github.com/neuralmind-ai/desafio-nm-estagio-de-verao-2026), utilizando a base fornecida pelo desafio como ponto de partida.

## Funcionalidades

- **Pipeline RAG completo** — Web scraping assíncrono (HTML e PDF), ingestão de documentos no Chroma DB com embeddings OpenAI, e busca por similaridade com reescrita de queries (expansão, simplificação, reformulação e estratégia combinada).
- **Streaming de respostas em tempo real** — Respostas da IA transmitidas via Server-Sent Events (SSE) com indicador de carregamento e botão de parar.
- **Persistência de conversas** — Histórico completo de chats e mensagens armazenado em PostgreSQL, com possibilidade de retomar conversas anteriores.
- **Títulos automáticos** — Geração automática de títulos descritivos para cada conversa via IA.
- **Autenticação via GitHub OAuth 2.0** — Fluxo OAuth completo com tokens JWT e cookies seguros.
- **Geração de relatórios** — Endpoint para geração de relatórios em PDF.
- **Interface responsiva** — UI com tema claro/escuro, sidebar retrátil, renderização Markdown e design mobile-friendly.
- **Deploy via Docker** — Orquestração de todos os serviços (backend, frontend, banco de dados) com Docker Compose.

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

- [Backend README](backend/README.md) — Detalhes da API, pipeline RAG, modelos e comandos de desenvolvimento.
- [Frontend README](frontend/README.md) — Detalhes da interface, componentes e comandos de desenvolvimento.

## Autor

**Miguel Ramos** — [GitHub](https://github.com/miguel-pramos)

Projeto desenvolvido como parte do [Desafio Estágio Verão 2026 da NeuralMind](https://github.com/neuralmind-ai/desafio-nm-estagio-de-verao-2026).

---

[Licença](LICENSE) | [Política de Segurança](SECURITY.md)
