# Arquitetura

## Objetivo

O Koru Bank é um simulador de atendimento bancário criado para demonstrar uma arquitetura Full Stack evolutiva. A aplicação separa UI, transporte HTTP, estado de conversa, regras de negócio, automações e futura integração com IA.

## Componentes

### Frontend

Responsável somente por experiência do usuário e estado efêmero de interface. O fluxo conversacional não é decidido no navegador; toda decisão de negócio vem da API.

### API FastAPI

Expõe contratos tipados para sessão, chat e operações. A API não mantém uma FSM global em memória. Cada conversa possui um identificador próprio e estado persistido.

### Conversation Service

Centraliza a máquina de estados do atendimento. O serviço recebe uma mensagem, classifica a intenção, aplica regras/guardrails, atualiza o estado e registra mensagens/eventos.

### Intent Router

Hoje utiliza `RuleIntentClassifier`. A abstração `IntentProvider` permite introduzir posteriormente um classificador baseado em LLM sem alterar as rotas HTTP ou a máquina de estados.

### Automation Service

Registra eventos operacionais como:

- `lead_captured`
- `handoff_requested`
- `transfer_simulated`
- `high_value_transfer_review`

A ideia é manter automações separadas do texto de resposta do chatbot, permitindo futuramente integrar filas, webhooks, workers ou sistemas externos.

### Banco de dados

SQLite é o padrão para facilitar avaliação local. `DATABASE_URL` pode apontar para PostgreSQL/Supabase sem alterar a camada de domínio.

## Segurança do case

- Não há operação bancária real.
- CPF é usado apenas para demonstrar validação e criação de sessão.
- O CPF não é persistido em texto puro.
- Transferências são simulações e exigem confirmação.
- Valores altos acionam revisão manual em vez de execução automática.
- IA permanece desabilitada até haver provedor, contratos de saída e testes específicos.

## Evolução sugerida

1. PostgreSQL/Supabase em produção.
2. Autenticação real com provedor de identidade, sem usar CPF como senha.
3. Redis para sessão/cache quando necessário.
4. Worker/fila para automações assíncronas.
5. Provedor de IA com structured output.
6. Observabilidade com tracing, métricas e error monitoring.
