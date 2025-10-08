import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  },

  register: async (data: {
    email: string
    username: string
    password: string
    full_name?: string
  }) => {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
}

// Nodes API
export const nodesApi = {
  list: async () => {
    const response = await api.get('/nodes/')
    return response.data
  },

  get: async (id: string) => {
    const response = await api.get(`/nodes/${id}`)
    return response.data
  },

  create: async (data: {
    id: string
    type: string
    label: string
    properties?: Record<string, string>
  }) => {
    const response = await api.post('/nodes/', data)
    return response.data
  },

  update: async (id: string, properties: Record<string, string>) => {
    const response = await api.patch(`/nodes/${id}`, { properties })
    return response.data
  },

  delete: async (id: string) => {
    const response = await api.delete(`/nodes/${id}`)
    return response.data
  },

  search: async (query: string) => {
    const response = await api.get('/nodes/search', { params: { q: query } })
    return response.data
  },

  stats: async () => {
    const response = await api.get('/nodes/stats')
    return response.data
  },
}
