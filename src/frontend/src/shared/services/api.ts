import axios, { AxiosError } from 'axios'
import type { AxiosInstance } from 'axios'
import { useAuthStore } from '@/modules/auth/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1'

// Token 刷新狀態管理
let isRefreshing = false
let failedQueue: Array<(token: string) => void> = []

const processQueue = (token: string) => {
  failedQueue.forEach((prom) => prom(token))
  failedQueue = []
}
class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // 請求攔截器
    this.client.interceptors.request.use((config) => {
      const authStore = useAuthStore()
      if (authStore.token) {
        config.headers.Authorization = `Bearer ${authStore.token}`
      }
      return config
    })

    // 響應攔截器 - 實現自動刷新
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any

        // 檢查是否是 401 且尚未重試過
        if (error.response?.status === 401 && !originalRequest._retry) {
          // 標記此請求已重試過，避免無限迴圈
          originalRequest._retry = true

          if (!isRefreshing) {
            isRefreshing = true

            try {
              // 嘗試刷新 token
              const response = await this.client.post('/auth/refresh')
              const { token } = response.data

              const authStore = useAuthStore()
              authStore.setToken(token)

              // 將新 token 應用到原請求
              originalRequest.headers.Authorization = `Bearer ${token}`

              // 處理隊列中的其他請求
              processQueue(token)

              // 重試原請求
              return this.client(originalRequest)
            } catch (error) {
              // 刷新失敗，執行登出
              const authStore = useAuthStore()
              authStore.logout()
              window.location.href = '/login'
              return Promise.reject(error)
            } finally {
              isRefreshing = false
            }
          } else {
            // 如果正在刷新，將此請求加入隊列
            return new Promise((resolve) => {
              failedQueue.push((token: string) => {
                originalRequest.headers.Authorization = `Bearer ${token}`
                resolve(this.client(originalRequest))
              })
            })
          }
        }

        return this.client.get<T>(url, config)
      },
    )
  }

  get<T = any>(url: string, config?: any) {
    return this.client.get<T>(url, config)
  }

  post<T = any>(url: string, data?: any, config?: any) {
    return this.client.post<T>(url, data, config)
  }

  put<T = any>(url: string, data?: any, config?: any) {
    return this.client.put<T>(url, data, config)
  }

  delete<T = any>(url: string, config?: any) {
    return this.client.delete<T>(url, config)
  }

  patch<T = any>(url: string, data?: any, config?: any) {
    return this.client.patch<T>(url, data, config)
  }
}

export default new ApiClient()
