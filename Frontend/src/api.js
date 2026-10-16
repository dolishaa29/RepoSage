// In dev, Vite proxies /auth to the backend. For a production build set
// VITE_API_URL to the backend origin (e.g. https://api.example.com).
const BASE = import.meta.env.VITE_API_URL || ''
const TOKEN_KEY = 'gitaudit_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

async function request(path, { method = 'GET', body } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  let res
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new Error('Cannot reach the server. Is the backend running?')
  }

  const data = await res.json().catch(() => null)
  if (!res.ok) {
    let msg = data?.detail ?? `Request failed (${res.status})`
    if (Array.isArray(msg)) msg = msg.map((d) => d.msg).join(', ')
    throw new Error(msg)
  }
  return data
}

export const api = {
  register: (name, email, password) => request('/auth/register', { method: 'POST', body: { name, email, password } }),
  login: (email, password) => request('/auth/login', { method: 'POST', body: { email, password } }),
  me: () => request('/auth/me'),
}
