import { useEffect, useState } from 'react'
import { api, clearToken, getToken, setToken } from './api'
import { navigate, useRoute } from './router'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import './App.css'

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
  if (!user) return route === 'register' ? <Register /> : <Login onLogin={onLogin} />

  return <Dashboard user={user} onLogout={logout} />
}

export default App
