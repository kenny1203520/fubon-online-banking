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
  
  logout: (tokenId: string) => 
    apiClient.post<LogoutResponse>('/auth/logout', { token_id: tokenId }),
  
  getCurrentUser: () => 
    apiClient.get<User>('/auth/me'),
  
  resetPassword: (username: string, email: string) => 
    apiClient.post('/auth/reset-password', { username, email }),

  refreshToken: () => 
    apiClient.post('/auth/refresh'),

  verify: () => 
    apiClient.post('/auth/verify'),
}
