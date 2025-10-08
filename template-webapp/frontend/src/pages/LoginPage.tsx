import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const { login, isLoading, error } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    try {
      await login({ username, password })
      navigate('/')
    } catch (err) {
      console.error('Login failed:', err)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Template WebApp</h1>
        <p>Sign in to your account</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="error-message">
              Login failed. Please check your credentials.
            </div>
          )}

          <button type="submit" disabled={isLoading} className="btn-primary">
            {isLoading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div className="login-footer">
          <p>
            Default credentials: <strong>admin</strong> / <strong>admin</strong>
          </p>
        </div>
      </div>
    </div>
  )
}
