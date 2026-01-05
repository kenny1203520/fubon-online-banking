export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  message: string
  code: number
}

export interface RegisterRequest {
  username: string
  password: string
  email?: string
}

export interface RegisterResponse {
  user_id: number
  username: string
  message: string
  code: number
}

export interface LogoutRequest {
  token: string
}

export interface LogoutResponse {
  message: string
  code: number
}

export interface User {
  id: number
  username: string
  email?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}
