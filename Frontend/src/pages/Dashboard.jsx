export default function Dashboard({ user, onLogout }) {
  return (
    <div className="layout">
      <header className="topbar">
        <a href="#/" className="brand">
          <span className="brand-mark">◆</span> gitAudit
        </a>
        <div className="topbar-right">
          <span className="muted">Hi, {user.name}</span>
          <button className="btn ghost" onClick={onLogout}>Log out</button>
        </div>
      </header>
      <main className="content">
        <section className="card">
          <h2>Dashboard</h2>
          <p className="muted">You are logged in.</p>
          <dl className="profile">
            <dt>Name</dt>
            <dd>{user.name}</dd>
            <dt>Email</dt>
            <dd>{user.email}</dd>
          </dl>
        </section>
      </main>
    </div>
  )
}
