# Case Study — evolução do Koru Bank

## Problema inicial

O protótipo original possuía uma UI em React com a lógica de conversa dentro do componente e uma versão separada em Flask com uma única FSM compartilhada. Essa abordagem funcionava como demonstração, mas limitava concorrência, testes, persistência e evolução para IA.

## Decisões da evolução

### 1. Consolidar frontend e backend

O React passa a ser exclusivamente cliente da API. A lógica conversacional fica no backend para permitir consistência, auditoria e múltiplas sessões.

### 2. Trocar estado global por conversa persistida

Cada usuário recebe um `session_id` e cada sessão possui sua própria conversa. Isso elimina interferência entre usuários e deixa o serviço preparado para múltiplas instâncias.

### 3. Corrigir classificação de intenção

A ordem das regras foi redesenhada para evitar que frases como "quero ser cliente" sejam classificadas apenas por conter a palavra "cliente".

### 4. Automatizar sem fingir que é IA

A versão atual é explicitamente rule-based. A camada de automações registra eventos e os torna visíveis no dashboard. A IA será adicionada depois, por contrato, sem substituir guardrails.

### 5. Projetar para demonstração segura

Saldo e transferências são fictícios. O projeto demonstra o fluxo arquitetural sem representar uma implementação bancária de produção.

## Pontos fortes para explicar em entrevista

- por que estado global em chatbot é um problema;
- diferença entre regra determinística e IA;
- por que IA não deve executar operação sensível diretamente;
- uso de confirmação e guardrails;
- separação entre domínio, API, persistência e UI;
- como migrar SQLite para PostgreSQL;
- como transformar eventos síncronos em automações assíncronas;
- como medir a futura camada de IA antes de promovê-la para produção.
