import { useAuth } from '../contexts/AuthContext'
import { useNodeStats } from '../hooks/useNodes'

export default function DashboardPage() {
  const { user } = useAuth()
  const { data: stats, isLoading } = useNodeStats()

  return (
    <div className="dashboard-page">
      <h1>Dashboard</h1>

      <div className="welcome-section">
        <h2>Welcome back, {user?.full_name || user?.username}!</h2>
        <p>Here's an overview of your data.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>User Info</h3>
          <div>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Username:</strong> {user?.username}</p>
            <p><strong>Role:</strong> {user?.is_superuser ? 'Admin' : 'User'}</p>
          </div>
        </div>

        <div className="stat-card">
          <h3>RDF Graph Statistics</h3>
          {isLoading ? (
            <p>Loading...</p>
          ) : (
            <div>
              {stats?.stats && stats.stats.length > 0 ? (
                <ul>
                  {stats.stats.map((stat: any) => (
                    <li key={stat.type}>
                      <strong>{stat.type.split('#').pop()}:</strong> {stat.count} nodes
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No data in RDF graph yet.</p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <a href="/nodes" className="btn-secondary">View Nodes</a>
          <a href="http://localhost:3030" target="_blank" rel="noopener noreferrer" className="btn-secondary">
            Open Fuseki UI
          </a>
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="btn-secondary">
            API Documentation
          </a>
        </div>
      </div>
    </div>
  )
}
