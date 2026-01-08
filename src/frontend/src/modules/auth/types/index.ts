export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token_id: string
  token: string
  expires_in: number
  code: number
}

export interface RegisterRequest {
  username: string
  password: string
  email?: string
  admin_code?: string
  role?: UserRole
}

export interface RegisterResponse {
  user_id: string
  username: string
  message: string
}

export interface LogoutRequest {
  token_id: string
}

export interface LogoutResponse {
  message: string
}

export type UserRole = 'user' | 'admin'

export interface User {
  user_id: string
  username: string
  email?: string
  role?: UserRole
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}
