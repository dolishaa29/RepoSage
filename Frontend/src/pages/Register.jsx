import { useState } from 'react'
import { api } from '../api'
import { navigate } from '../router'

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.register(form.name, form.email, form.password)
      navigate('/login')
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
        <p className="muted">Create a new account.</p>

        <form onSubmit={submit} className="form">
          <label>
            Name
            <input value={form.name} onChange={update('name')} required autoComplete="name" />
          </label>
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
              minLength={6}
              autoComplete="new-password"
            />
          </label>
          {error && <div className="alert error">{error}</div>}
          <button className="btn primary" disabled={loading}>
            {loading ? 'Please wait…' : 'Create account'}
          </button>
        </form>

        <p className="muted switch">
          Already have an account? <a href="#/login">Log in</a>
        </p>
      </div>
    </div>
  )
}
