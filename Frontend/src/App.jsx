import { useEffect, useState } from 'react'
import { api, clearToken, getToken, setToken } from './api'
import { navigate, useRoute } from './router'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import './App.css'

// GitHub login comes back as #/github?token=... and failures as #/?error=...
const redirect = new URLSearchParams(window.location.hash.split('?')[1] || '')
if (redirect.get('token')) setToken(redirect.get('token'))
const redirectError = redirect.get('error') || ''
if (window.location.hash.includes('?')) history.replaceState(null, '', '#/')

function App() {
  const [user, setUser] = useState(null)
  const [checking, setChecking] = useState(Boolean(getToken()))
  const route = useRoute()

  useEffect(() => {
    if (!getToken()) return
    api
      .me()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setChecking(false))
  }, [])

  const onLogin = async (token) => {
    setToken(token)
    setUser(await api.me())
    navigate('/')
  }

  const logout = () => {
    clearToken()
    setUser(null)
    navigate('/login')
  }

  if (checking) return <div className="center muted">Loading…</div>
  if (!user) {
    return route === 'register' ? <Register notice={redirectError} /> : <Login onLogin={onLogin} notice={redirectError} />
  }

  return <Dashboard user={user} onLogout={logout} notice={redirectError} />
}

export default App
