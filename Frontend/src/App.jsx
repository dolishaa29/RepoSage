import { useEffect, useState } from 'react'
import { api, clearToken, getToken, setToken } from './api'
import { navigate, useRoute } from './router'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import './App.css'

// Runs once when the page opens and returns the logged-in user (or null).
async function loadUser() {
  // coming back from GitHub? the URL looks like /?code=...&state=...
  const params = new URLSearchParams(window.location.search)
  const code = params.get('code')

  if (code) {
    window.history.replaceState(null, '', '/') // remove ?code from the address bar
    if (params.get('state') !== sessionStorage.getItem('github_state')) {
      throw new Error('GitHub login failed, please try again')
    }
    if (getToken()) {
      await api.githubConnect(code) // already logged in -> connect GitHub
    } else {
      const { access_token } = await api.githubLogin(code) // logged out -> log in with GitHub
      setToken(access_token)
    }
  }

  if (!getToken()) return null
  return api.me()
}

const userPromise = loadUser()

function App() {
  const [user, setUser] = useState(null)
  const [checking, setChecking] = useState(true)
  const [error, setError] = useState('')
  const route = useRoute()

  useEffect(() => {
    userPromise
      .then(setUser)
      .catch((err) => setError(err.message))
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
    return route === 'register' ? <Register notice={error} /> : <Login onLogin={onLogin} notice={error} />
  }

  return <Dashboard user={user} onLogout={logout} notice={error} />
}

export default App
