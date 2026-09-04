import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppHeader from '../components/AppHeader'
import Brand from '../components/Brand'
import LoadingDots from '../components/LoadingDots'
import { sendMessage, startConversation } from '../services/api'

function Message({ role, content }) {
  return (
    <div className={`message-row message-row--${role}`}>
      {role === 'assistant' && <div className="avatar-mark">K</div>}
      <div className="message-bubble">{content}</div>
    </div>
  )
}

export default function ChatPage() {
  const navigate = useNavigate()
  const sessionId = sessionStorage.getItem('koru_session_id')
  const maskedCpf = sessionStorage.getItem('koru_masked_cpf')
  const [messages, setMessages] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [meta, setMeta] = useState({ state: 'starting', intent: null, confidence: null })
  const boxRef = useRef(null)
  const startedRef = useRef(false)

  useEffect(() => {
    if (!sessionId) {
      navigate('/', { replace: true })
      return
    }
    if (startedRef.current) return
    startedRef.current = true

    startConversation(sessionId)
      .then((payload) => {
        setMessages([{ role: 'assistant', content: payload.message }])
        setSuggestions(payload.suggestions || [])
        setMeta(payload)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [navigate, sessionId])

  useEffect(() => {
    if (boxRef.current) boxRef.current.scrollTop = boxRef.current.scrollHeight
  }, [messages, loading])

  async function submitMessage(message) {
    const clean = message.trim()
    if (!clean || loading) return

    setMessages((current) => [...current, { role: 'user', content: clean }])
    setInput('')
    setSuggestions([])
    setError('')

    try {
      setLoading(true)
      const payload = await sendMessage(sessionId, clean)
      setMessages((current) => [...current, { role: 'assistant', content: payload.message }])
      setSuggestions(payload.suggestions || [])
      setMeta(payload)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    submitMessage(input)
  }

  function resetSession() {
    sessionStorage.removeItem('koru_session_id')
    sessionStorage.removeItem('koru_masked_cpf')
    navigate('/')
  }

  return (
    <div className="page-shell page-shell--app">
      <AppHeader />
      <main className="workspace">
        <aside className="context-panel">
          <Brand />
          <p className="context-panel__intro">
            Atendimento demonstrativo com decisões no backend, estado por sessão e eventos auditáveis.
          </p>

          <div className="architecture-list">
            <div><span>01</span><p><strong>Intent Router</strong><small>regras determinísticas</small></p></div>
            <div><span>02</span><p><strong>Guardrails</strong><small>confirmações e limites</small></p></div>
            <div><span>03</span><p><strong>Automations</strong><small>eventos operacionais</small></p></div>
            <div className="architecture-list__muted"><span>04</span><p><strong>AI Provider</strong><small>preparado · desativado</small></p></div>
          </div>

          <div className="session-card">
            <small>SESSÃO DEMO</small>
            <strong>{maskedCpf || 'CPF mascarado'}</strong>
            <span>{sessionId?.slice(0, 8)}...</span>
          </div>

          <button className="text-button" type="button" onClick={resetSession}>Encerrar demonstração</button>
        </aside>

        <section className="chat-panel">
          <div className="chat-panel__header">
            <div className="chat-identity">
              <div className="avatar-mark avatar-mark--large">K</div>
              <div>
                <h2>Assistente Koru</h2>
                <p><span className="status-dot" /> Online · rule-based</p>
              </div>
            </div>
            <div className="chat-meta">
              <span>state: {meta.state || '—'}</span>
              {meta.intent && <span>intent: {meta.intent}</span>}
            </div>
          </div>

          <div className="chat-transcript" ref={boxRef} aria-live="polite">
            <div className="chat-notice">
              Esta é uma simulação. Não envie dados pessoais, senhas ou informações bancárias reais.
            </div>
            {messages.map((message, index) => <Message key={`${message.role}-${index}`} {...message} />)}
            {loading && messages.length > 0 && (
              <div className="message-row message-row--assistant">
                <div className="avatar-mark">K</div>
                <div className="message-bubble"><LoadingDots /></div>
              </div>
            )}
            {error && <div className="chat-error">{error}</div>}
          </div>

          {suggestions.length > 0 && (
            <div className="suggestion-row">
              {suggestions.map((suggestion) => (
                <button key={suggestion} type="button" onClick={() => submitMessage(suggestion)} disabled={loading}>
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          <form className="chat-composer" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Digite sua mensagem..."
              autoFocus
              maxLength={300}
            />
            <button type="submit" disabled={loading || !input.trim()}>Enviar <span>↗</span></button>
          </form>
        </section>
      </main>
    </div>
  )
}
