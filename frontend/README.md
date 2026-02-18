# Frontend — Unicamp VestIA

Interface frontend em Next.js para o chatbot Unicamp VestIA, oferecendo uma experiência de chat em tempo real com respostas fundamentadas sobre o Vestibular Unicamp 2026. Desenvolvido a partir da base do [Desafio Estágio Verão 2026 da NeuralMind](https://github.com/neuralmind-ai/desafio-nm-estagio-de-verao-2026).

## Funcionalidades Desenvolvidas

- **Chat em tempo real** — Streaming de respostas com indicador de carregamento e botão de parar
- **Renderização Markdown** — Respostas formatadas com GitHub Flavored Markdown
- **Gestão de conversas** — Sidebar com histórico de chats, títulos automáticos, pré-visualização da última mensagem, criação e exclusão de conversas
- **Autenticação GitHub** — Login via GitHub OAuth, perfil do usuário (avatar, nome), logout e rotas protegidas
- **Tema claro/escuro** — Alternância de tema com persistência
- **Design responsivo** — Interface adaptada para desktop e mobile com sidebar retrátil
- **Tela de boas-vindas** — Página overview com descrição das funcionalidades do chatbot

## Stack

- [**Next.js 15 App Router**](https://nextjs.org/docs) com [**React 19**](https://react.dev/)
- [**TypeScript**](https://www.typescriptlang.org/) — Tipagem estática
- [**Tailwind CSS**](https://tailwindcss.com/) + [**shadcn/ui**](https://ui.shadcn.com/) (Radix UI) — Estilização e componentes
- [**AI SDK React**](https://ai-sdk.dev/) — Integração com streaming de IA
- [**React Markdown**](https://github.com/remarkjs/react-markdown) — Renderização de Markdown
- [**OpenAPI Generator (typescript-fetch)**](https://openapi-ts.dev/openapi-fetch/) — Cliente tipado gerado a partir da API
- [**Zod**](https://zod.dev/) + [**@t3-oss/env-nextjs**](https://env.t3.gg/) — Validação de schemas e variáveis de ambiente
- [**Node.js 20+**](https://nodejs.org/) com [**pnpm**](https://pnpm.io/)

## Pré-requisitos

- Node.js 20+
- pnpm

## Início Rápido

1. Instale as dependências:

   ```bash
   pnpm install
   ```

2. Configure o ambiente (crie `.env` na raiz do frontend):

   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

   Ajuste a URL da API conforme necessário. Leia o conteúdo do arquivo `src/env.ts` para mais informações sobre as variáveis de ambiente.

   **Nota:** Isso requer que a API backend esteja rodando e acessível na URL configurada.

3. **Inicie o servidor de desenvolvimento:**
   ```bash
   pnpm dev
   ```

A aplicação estará disponível em `http://localhost:3000`.

## Estrutura de Pastas

```
frontend/
├── src/
│   ├── actions/              # Server Actions (autenticação)
│   ├── app/                  # App Router do Next.js
│   │   ├── (auth)/           # Rotas de autenticação (sign-in)
│   │   ├── (chat)/           # Rotas do chat (protegidas)
│   │   │   └── chat/[id]/    # Página de chat por ID
│   │   ├── api/              # API Routes (proxy chat, cookies)
│   │   ├── layout.tsx        # Layout raiz
│   │   └── page.tsx          # Página inicial
│   ├── components/           # Componentes reutilizáveis
│   │   ├── auth/             # Componentes de autenticação
│   │   ├── ai/               # Componentes do chat e IA
│   │   └── ui/               # Componentes UI (shadcn/ui)
│   ├── contexts/             # Contextos React (usuário)
│   ├── hooks/                # Hooks customizados (scroll, mobile)
│   ├── lib/                  # Utilitários e cliente da API
│   │   ├── api/              # Funções utilitárias (IA, auth)
│   │   └── api-client.gen/   # Cliente gerado via OpenAPI
│   ├── styles/               # Estilos globais
│   └── env.ts                # Validação de variáveis de ambiente
└── public/                   # Arquivos estáticos
```

## Comandos Úteis

| Comando              | Descrição                                    |
| -------------------- | -------------------------------------------- |
| `pnpm dev`           | Inicia o servidor de desenvolvimento         |
| `pnpm build`         | Constrói a aplicação para produção           |
| `pnpm start`         | Inicia o servidor de produção (após build)   |
| `pnpm lint`          | Executa o linter                             |
| `pnpm format:check`  | Verifica a formatação do código             |
| `pnpm typecheck`     | Verifica tipos TypeScript                    |
| `pnpm test`          | Executa os testes automatizados              |
| `pnpm apigen`        | Gera o cliente da API a partir do OpenAPI    |

**Notas:**

- Reexecute `pnpm apigen` sempre que o backend for atualizado. O cliente gerado em `src/lib/api-client.gen` é substituído.
- O comando `pnpm apigen` lê `NEXT_PUBLIC_API_URL` do `.env` e usa o endpoint `${NEXT_PUBLIC_API_URL}/openapi.json`.
