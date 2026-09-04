# Roadmap de IA

A arquitetura já possui uma fronteira explícita para IA, mas a versão atual não depende de LLM.

## Princípio

O modelo não deve controlar diretamente operações financeiras. Ele interpreta linguagem natural e devolve uma saída estruturada. O backend continua responsável por autorização, validação, limites, confirmação e execução.

## Fase 1 — Classificação estruturada

Entrada:

```text
"Quero mandar duzentos reais para Maria"
```

Saída esperada do provedor:

```json
{
  "intent": "transfer",
  "confidence": 0.96,
  "entities": {
    "amount": 200,
    "recipient": "Maria"
  }
}
```

A resposta deve ser validada por schema antes de chegar ao domínio.

## Fase 2 — Roteamento híbrido

- Regras continuam cobrindo comandos simples e críticos.
- IA atua em linguagem ambígua ou livre.
- Baixa confiança gera fallback ou handoff.
- Métricas comparam acerto por regras vs. IA.

## Fase 3 — Tool calling controlado

Ferramentas candidatas:

- `get_demo_balance(session_id)`
- `prepare_transfer(amount, recipient)`
- `request_human_handoff(reason)`

Nenhuma ferramenta sensível deve ser executada sem autorização do backend e confirmação explícita do usuário.

## Fase 4 — Avaliação

Adicionar dataset de intents e testes de regressão para medir:

- precisão por intenção;
- taxa de fallback;
- falsos positivos em operações sensíveis;
- latência;
- custo por conversa;
- taxa de handoff.
