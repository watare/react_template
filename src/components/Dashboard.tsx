import { useState, useEffect } from 'react'
import { DashboardData, Activity } from '../types'
import './Dashboard.css'

interface DashboardProps {
  username: string;
  onLogout: () => void;
}

/**
 * Dashboard Component
 * Demonstrates:
 * - useState for managing component state
 * - useEffect for side effects (simulating data fetch)
 * - Working with mock data
 * - Component composition
 */
const Dashboard = ({ username, onLogout }: DashboardProps) => {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  // useEffect: Runs side effects after component renders
  // Empty dependency array [] means it runs only once (on mount)
  useEffect(() => {
    // Simulate API call to fetch dashboard data
    const fetchDashboardData = () => {
      setTimeout(() => {
        // Mock data
        const mockData: DashboardData = {
          totalUsers: 1247,
          activeProjects: 23,
          completedTasks: 184,
          recentActivity: [
            {
              id: '1',
              user: 'Alice Johnson',
              action: 'Completed project "Website Redesign"',
              timestamp: new Date(Date.now() - 1000 * 60 * 5), // 5 minutes ago
            },
            {
              id: '2',
              user: 'Bob Smith',
              action: 'Created new task "Update documentation"',
              timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
            },
            {
              id: '3',
              user: 'Carol White',
              action: 'Added comment to "API Integration"',
              timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
            },
            {
              id: '4',
              user: 'David Brown',
              action: 'Uploaded 5 new files to project',
              timestamp: new Date(Date.now() - 1000 * 60 * 45), // 45 minutes ago
            },
          ],
        }
        setData(mockData)
        setLoading(false)
      }, 1000) // 1 second delay to simulate network request
    }

    fetchDashboardData()
  }, []) // Empty dependency array: runs once on component mount

  const formatTimeAgo = (date: Date): string => {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000)

    if (seconds < 60) return `${seconds} seconds ago`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
    const hours = Math.floor(minutes / 60)
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  }

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading dashboard...</div>
      </div>
    )
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p className="welcome">Welcome back, {username}!</p>
        </div>
        <button onClick={onLogout} className="logout-button">
          Logout
        </button>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{data?.totalUsers.toLocaleString()}</div>
          <div className="stat-label">Total Users</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data?.activeProjects}</div>
          <div className="stat-label">Active Projects</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data?.completedTasks}</div>
          <div className="stat-label">Completed Tasks</div>
        </div>
      </div>

      <div className="activity-section">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          {data?.recentActivity.map((activity: Activity) => (
            <div key={activity.id} className="activity-item">
              <div className="activity-content">
                <strong>{activity.user}</strong>
                <span className="activity-action">{activity.action}</span>
              </div>
              <div className="activity-time">
                {formatTimeAgo(activity.timestamp)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
