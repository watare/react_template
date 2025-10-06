import { useState } from 'react'
import Login from './components/Login'
import Dashboard from './components/Dashboard'

/**
 * App Component
 * Demonstrates:
 * - Application state management
 * - Conditional rendering
 * - Passing props to child components
 * - Callback functions for child-to-parent communication
 */
function App() {
  // State to track if user is logged in and their username
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentUser, setCurrentUser] = useState('')

  // Handler for successful login
  const handleLogin = (username: string) => {
    setCurrentUser(username)
    setIsLoggedIn(true)
  }

  // Handler for logout
  const handleLogout = () => {
    setIsLoggedIn(false)
    setCurrentUser('')
  }

  // Conditional rendering: Show Dashboard if logged in, otherwise show Login
  return (
    <>
      {isLoggedIn ? (
        <Dashboard username={currentUser} onLogout={handleLogout} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </>
  )
}

export default App
