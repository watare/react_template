import { useState } from 'react'
import './Login.css'

interface LoginProps {
  onLogin: (username: string) => void;
}

/**
 * Login Component
 * Demonstrates:
 * - useState hook for managing form state
 * - Event handlers for user input
 * - Controlled components (inputs bound to state)
 * - Props for parent communication
 */
const Login = ({ onLogin }: LoginProps) => {
  // useState: Creates state variables for username and password
  // Returns [currentValue, setterFunction]
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault() // Prevent page reload on form submit

    // Simple validation (mock authentication)
    if (username.trim() === '' || password.trim() === '') {
      setError('Please fill in all fields')
      return
    }

    if (password.length < 4) {
      setError('Password must be at least 4 characters')
      return
    }

    // Mock successful login
    setError('')
    onLogin(username)
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Welcome Back</h1>
        <p className="subtitle">Sign in to your account</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button">
            Sign In
          </button>
        </form>

        <div className="hint">
          <small>Hint: Use any username with password length ≥ 4</small>
        </div>
      </div>
    </div>
  )
}

export default Login
