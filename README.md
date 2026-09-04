# Koru Bank — Full Stack Banking Assistant

Case de portfólio que evolui o protótipo original do Koru Bank para uma aplicação **Full Stack**, com frontend em React, API em FastAPI, persistência de sessões/conversas, automações orientadas a eventos, testes e arquitetura preparada para integração futura com IA.

> **Importante:** este projeto é uma simulação educacional. Não executa operações bancárias reais, não deve receber dados pessoais reais e não implementa autenticação bancária de produção.

## Destaques

- React + Vite com experiência responsiva e fluxo de atendimento
- FastAPI com schemas tipados, CORS e documentação OpenAPI automática
- Validação real do algoritmo de CPF para o fluxo demonstrativo
- Sessão independente por usuário; nenhum estado global compartilhado entre conversas
- Persistência em SQLite por padrão e configuração pronta para PostgreSQL/Supabase
- Chatbot determinístico baseado em regras, com classificação de intenção testável
- Fluxo simulado de saldo, transferência com confirmação e handoff humano
- Guardrail de transferência de alto valor para revisão manual
- Automação orientada a eventos e trilha de auditoria
- Dashboard operacional com métricas e eventos recentes
- Camada `ai/` pronta para receber um provedor de IA, mas **desativada nesta versão**
- Testes backend e pipeline de CI no GitHub Actions
- Docker para subir frontend + backend com um único comando

## Arquitetura

```text
React / Vite
    |
    | HTTP JSON
    v
FastAPI
    |
    +-- Session API
    +-- Chat API
    +-- Operations API
    |
    v
Conversation Service
    |
    +-- Rule Intent Classifier  <--- ativo
    +-- AI Provider Interface   <--- preparado / desativado
    +-- Automation Service
    +-- Guardrails
    |
    v
SQLAlchemy
    |
    +-- SQLite (local)
    +-- PostgreSQL / Supabase (configurável)
```

Detalhes: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Fluxos disponíveis

### Cliente existente

1. Inicia uma sessão com CPF fictício válido.
2. Informa o nome no chat.
3. Seleciona "Já sou cliente".
4. Pode consultar saldo fictício, simular transferência ou pedir atendimento humano.
5. Transferências acima do limite de demonstração são encaminhadas para revisão manual.

### Novo cliente

O fluxo registra apenas um **evento demonstrativo de interesse**, sem coletar dados adicionais. Em uma solução real, essa etapa seria substituída por onboarding/KYC integrado a serviços apropriados.

## Stack

| Camada | Tecnologias |
| --- | --- |
| Frontend | React 18, React Router, Vite |
| Backend | Python, FastAPI, Pydantic |
| Persistência | SQLAlchemy, SQLite; pronto para PostgreSQL |
| Qualidade | Pytest, Vitest, GitHub Actions |
| Infra | Docker, Nginx |
| IA | Interface preparada; integração não ativada |

## Executar com Docker

Pré-requisito: Docker Desktop.

```bash
docker compose up --build
```

Acesse:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger/OpenAPI: `http://localhost:8000/docs`

## Executar localmente sem Docker

### Backend

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

### Frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

## CPF para demonstração

Use apenas dados fictícios. Um exemplo de CPF matematicamente válido para teste é:

```text
529.982.247-25
```

A aplicação valida os dígitos verificadores. O backend não guarda o CPF em texto puro: a sessão armazena apenas hash e versão mascarada. Isso **não transforma o fluxo em autenticação bancária real**.

## Endpoints principais

| Método | Endpoint | Uso |
| --- | --- | --- |
| GET | `/api/v1/health` | Saúde e capabilities da API |
| POST | `/api/v1/sessions` | Cria sessão demonstrativa |
| POST | `/api/v1/chat/start` | Inicia/recupera conversa |
| POST | `/api/v1/chat/messages` | Processa mensagem |
| GET | `/api/v1/operations/dashboard` | Métricas operacionais |

## IA: pronta, mas sem conexão nesta versão

O projeto não apresenta regras como se fossem IA. A implementação atual usa um classificador determinístico e expõe uma fronteira clara para evolução futura:

```text
app/ai/base.py
app/ai/router.py
```

Quando a integração for feita, o LLM poderá atuar apenas na **interpretação da intenção/extração estruturada**, enquanto operações sensíveis continuarão controladas pelo backend, com validação, confirmação e guardrails.

Veja o plano em [`docs/AI_ROADMAP.md`](docs/AI_ROADMAP.md).

## Testes

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm install
npm test
```

## O que este case demonstra

Este repositório foi estruturado para evidenciar competências além da interface visual: separação de responsabilidades, desenho de API, modelagem de estado, persistência, validação, automação, guardrails, observabilidade básica, testes, CI e preparação para recursos de IA sem acoplar regras de negócio ao modelo.

Veja também [`docs/CASE_STUDY.md`](docs/CASE_STUDY.md) para decisões técnicas e pontos de apresentação em entrevista.
