import { useState } from 'react'
import { api } from '../api'

export default function Login({ onLogin }) {
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { access_token } = await api.login(form.email, form.password)
      await onLogin(access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card card">
        <div className="brand big">
          <span className="brand-mark">◆</span> gitAudit
        </div>
        <p className="muted">Log in to your account.</p>

        <form onSubmit={submit} className="form">
          <label>
            Email
            <input type="email" value={form.email} onChange={update('email')} required autoComplete="email" />
          </label>
          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={update('password')}
              required
              autoComplete="current-password"
            />
          </label>
          {error && <div className="alert error">{error}</div>}
          <button className="btn primary" disabled={loading}>
            {loading ? 'Please wait…' : 'Log in'}
          </button>
        </form>

        <p className="muted switch">
          New here? <a href="#/register">Create an account</a>
        </p>
      </div>
    </div>
  )
}
