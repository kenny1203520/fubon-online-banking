import apiClient from '../../../shared/services/api'
import type {
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  LogoutResponse,
  User
} from '../types'

export const authService = {
  login: (username: string, password: string) => 
    apiClient.post<LoginResponse>('/auth/login', { username, password }),
  
  register: (data: RegisterRequest) => 
    apiClient.post<RegisterResponse>('/auth/register', data),
  
  logout: () => 
    apiClient.post<LogoutResponse>('/auth/logout'),
  
  getCurrentUser: () => 
    apiClient.get<User>('/auth/me'),
  
  refreshToken: () => 
    apiClient.post('/auth/refresh'),
  
  resetPassword: (email: string) => 
    apiClient.post('/auth/reset-password', { email }),
  
  verifyToken: (token: string) => 
    apiClient.post('/auth/verify-token', { token }),
}
