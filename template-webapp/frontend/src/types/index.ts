export interface Role {
  id: number
  name: string
  description: string
}

export interface User {
  id: number
  email: string
  username: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  roles?: Role[]
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

export interface SCLFile {
  id: number
  filename: string
  original_filename: string
  file_size: number
  status: 'uploaded' | 'converting' | 'converted' | 'validated' | 'failed'
  is_validated: boolean
  validation_passed: boolean | null
  validation_message: string | null
  triple_count: number | null
  fuseki_dataset: string | null
  uploaded_by: string
  uploaded_at: string
  converted_at: string | null
  error_message: string | null
}
