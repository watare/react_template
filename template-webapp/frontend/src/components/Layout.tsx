import { Outlet, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="app-layout">
      <nav className="navbar">
        <div className="nav-brand">
          <h1>Template WebApp</h1>
        </div>

        <div className="nav-links">
          <Link to="/">Dashboard</Link>
          <Link to="/nodes">Nodes</Link>
          {(user?.is_superuser || user?.roles?.some((r: any) => r.name === 'admin')) && (
            <Link to="/scl-files">SCL Files</Link>
          )}
        </div>

        <div className="nav-user">
          <span>Welcome, {user?.username}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </nav>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
