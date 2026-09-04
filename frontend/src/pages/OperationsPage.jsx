import { useEffect, useState } from 'react'
import AppHeader from '../components/AppHeader'
import { getDashboard } from '../services/api'

const eventLabels = {
  session_created: 'Sessão criada',
  lead_captured: 'Lead demonstrativo',
  handoff_requested: 'Handoff humano',
  transfer_simulated: 'Transferência simulada',
  high_value_transfer_review: 'Revisão de alto valor',
}

function Metric({ label, value, detail }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  )
}

export default function OperationsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getDashboard().then(setData).catch((err) => setError(err.message))
  }, [])

  return (
    <div className="page-shell page-shell--operations">
      <AppHeader />
      <main className="operations-wrap">
        <div className="operations-heading">
          <div>
            <span className="eyebrow">AI OPERATIONS CENTER · DEMO</span>
            <h1>Operational overview</h1>
            <p>Métricas de sessões, conversas e automações registradas pelo backend.</p>
          </div>
          <div className="system-status"><span className="status-dot" /> API operational</div>
        </div>

        {error && <div className="panel-error">{error} Verifique se a API está em execução.</div>}
        {!data && !error && <div className="dashboard-loading">Carregando métricas...</div>}

        {data && (
          <>
            <section className="metrics-grid">
              <Metric label="Sessões" value={data.total_sessions} detail="criadas na demonstração" />
              <Metric label="Conversas ativas" value={data.active_conversations} detail="estado persistido" />
              <Metric label="Mensagens" value={data.total_messages} detail="auditáveis no backend" />
              <Metric label="Automações" value={data.automation_events} detail="eventos operacionais" />
              <Metric label="Handoffs" value={data.handoffs} detail="encaminhados ao humano" />
              <Metric label="Confiança média" value={`${Math.round((data.avg_intent_confidence || 0) * 100)}%`} detail="classificador por regras" />
            </section>

            <section className="operations-grid">
              <article className="ops-card">
                <div className="ops-card__header"><div><span>CONVERSATION STATES</span><h2>Distribuição atual</h2></div></div>
                <div className="state-list">
                  {Object.entries(data.states).length === 0 && <p className="empty-state">Nenhuma conversa ainda.</p>}
                  {Object.entries(data.states).map(([state, count]) => (
                    <div key={state}>
                      <span>{state}</span>
                      <div className="state-bar"><i style={{ width: `${Math.max(8, (count / Math.max(1, data.total_sessions)) * 100)}%` }} /></div>
                      <strong>{count}</strong>
                    </div>
                  ))}
                </div>
              </article>

              <article className="ops-card ops-card--events">
                <div className="ops-card__header"><div><span>EVENT STREAM</span><h2>Eventos recentes</h2></div><span className="live-pill">LIVE LOG</span></div>
                <div className="event-list">
                  {data.recent_events.length === 0 && <p className="empty-state">Use o assistente para gerar eventos.</p>}
                  {data.recent_events.map((event) => (
                    <div className="event-item" key={event.id}>
                      <span className="event-icon">↳</span>
                      <div><strong>{eventLabels[event.event_type] || event.event_type}</strong><small>{event.created_at.replace('T', ' ').slice(0, 19)}</small></div>
                      <code>{event.session_id.slice(0, 8)}</code>
                    </div>
                  ))}
                </div>
              </article>
            </section>

            <section className="capabilities-card">
              <div><span className="eyebrow">ARCHITECTURE STATUS</span><h2>IA preparada. Não conectada.</h2></div>
              <p>
                O classificador atual é determinístico. A interface de provedor permite introduzir IA depois sem dar ao modelo controle direto sobre operações sensíveis.
              </p>
              <div className="capability-tags"><span>Structured intents</span><span>Guardrails</span><span>Audit trail</span><span>Human handoff</span></div>
            </section>
          </>
        )}
      </main>
    </div>
  )
}
