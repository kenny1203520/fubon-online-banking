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
<<<<<<< HEAD
  admin_code?: string
  role?: UserRole
=======
  phone?: string
>>>>>>> d9ef812b699fa053b3951827ff5672c5cb5c8702
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
  phone?: string
  role?: UserRole
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}
