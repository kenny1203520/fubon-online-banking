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
}

export interface RegisterResponse {
  user_id: number
  username: string
  message: string
}

export interface LogoutRequest {
  token_id: string
}

export interface LogoutResponse {
  message: string
}

export interface User {
  user_id: number
  username: string
  email?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}
