import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { authApi } from '../services/api'

export interface User {
  id: number
  email: string
  username: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
}

interface AuthContextType {
  user: User | undefined
  isAuthenticated: boolean
  login: (credentials: { username: string; password: string }) => Promise<any>
  logout: () => void
  isLoading: boolean
  error: Error | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => !!localStorage.getItem('token')
  )

  const { data: user, refetch } = useQuery<User>({
    queryKey: ['currentUser'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated,
    retry: false,
  })

  const loginMutation = useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      authApi.login(username, password),
    onSuccess: (data) => {
      localStorage.setItem('token', data.access_token)
      setIsAuthenticated(true)
      refetch()
    },
  })

  const logout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
  }

  useEffect(() => {
    const token = localStorage.getItem('token')
    setIsAuthenticated(!!token)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        login: loginMutation.mutateAsync,
        logout,
        isLoading: loginMutation.isPending,
        error: loginMutation.error,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
