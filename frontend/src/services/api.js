const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  let payload = null
  try {
    payload = await response.json()
  } catch {
    payload = null
  }

  if (!response.ok) {
    const message = payload?.detail || payload?.message || 'Não foi possível concluir a operação.'
    throw new Error(typeof message === 'string' ? message : 'Erro inesperado na API.')
  }

  return payload
}

export function createSession(cpf) {
  return request('/api/v1/sessions', {
    method: 'POST',
    body: JSON.stringify({ cpf }),
  })
}

export function startConversation(sessionId) {
  return request('/api/v1/chat/start', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  })
}

export function sendMessage(sessionId, message) {
  return request('/api/v1/chat/messages', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, message }),
  })
}

export function getDashboard() {
  return request('/api/v1/operations/dashboard')
}

export { API_URL }
