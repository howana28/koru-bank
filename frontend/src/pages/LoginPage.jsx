import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppHeader from '../components/AppHeader'
import { createSession } from '../services/api'
import { formatCpf, isValidCpf } from '../utils/cpf'

export default function LoginPage() {
  const navigate = useNavigate()
  const [cpf, setCpf] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (!isValidCpf(cpf)) {
      setError('Digite um CPF fictício matematicamente válido para continuar.')
      return
    }

    try {
      setLoading(true)
      const session = await createSession(cpf)
      sessionStorage.setItem('koru_session_id', session.session_id)
      sessionStorage.setItem('koru_masked_cpf', session.masked_cpf)
      navigate('/chat')
    } catch (err) {
      setError(`${err.message} Verifique se a API está em execução.`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-shell page-shell--home">
      <AppHeader />

      <main className="hero-grid">
        <section className="hero-copy">
          <div className="eyebrow">BANKING EXPERIENCE · FULL STACK CASE</div>
          <h1>
            Um banco digital que trata cada conversa como <span>única.</span>
          </h1>
          <p className="hero-description">
            Uma experiência demonstrativa de atendimento bancário com arquitetura preparada
            para automações, observabilidade e uma futura camada de IA com guardrails.
          </p>

          <div className="feature-row" aria-label="Destaques técnicos">
            <span>React + FastAPI</span>
            <span>Automations</span>
            <span>AI-ready</span>
          </div>

          <form className="access-card" onSubmit={handleSubmit} noValidate>
            <div>
              <label htmlFor="cpf">Acessar demonstração</label>
              <p>Use somente um CPF fictício válido. Ex.: 529.982.247-25</p>
            </div>
            <div className={`cpf-control ${error ? 'cpf-control--error' : ''}`}>
              <input
                id="cpf"
                value={cpf}
                onChange={(event) => setCpf(formatCpf(event.target.value))}
                inputMode="numeric"
                autoComplete="off"
                placeholder="000.000.000-00"
                aria-describedby={error ? 'cpf-error' : undefined}
              />
              <button type="submit" disabled={loading} aria-label="Entrar na demonstração">
                {loading ? '...' : '→'}
              </button>
            </div>
            {error && <p className="form-error" id="cpf-error">{error}</p>}
          </form>
        </section>

        <section className="hero-visual" aria-label="Visual do produto">
          <div className="orb orb--one" />
          <div className="orb orb--two" />
          <div className="bank-card bank-card--back">
            <span>KORU</span>
          </div>
          <div className="bank-card bank-card--front">
            <div className="bank-card__top">
              <span className="mini-mark">K</span>
              <span>DEMO ACCOUNT</span>
            </div>
            <div className="bank-card__balance">
              <small>Saldo demonstrativo</small>
              <strong>R$ 2.430,70</strong>
            </div>
            <div className="bank-card__bottom">
              <span>•••• 2026</span>
              <span>PORTFOLIO</span>
            </div>
          </div>
          <div className="floating-card floating-card--automation">
            <span className="status-dot" />
            <div><strong>Automation Engine</strong><small>event-driven · ativo</small></div>
          </div>
          <div className="floating-card floating-card--ai">
            <span className="spark">✦</span>
            <div><strong>AI layer</strong><small>prepared · disabled</small></div>
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <span>KORU BANK · PORTFOLIO CASE 2026</span>
        <span>Simulação educacional · sem operações financeiras reais</span>
      </footer>
    </div>
  )
}
