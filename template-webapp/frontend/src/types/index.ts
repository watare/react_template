export interface User {
  id: number
  email: string
  username: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface Node {
  id: string
  type?: string
  label?: string
  properties?: Record<string, any>
}
