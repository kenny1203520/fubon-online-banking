import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services/auth'
import type { User } from '../types'

const TOKEN_ID_KEY = 'auth_token_id'
const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

export const useAuthStore = defineStore('auth', () => {
  // State
  const tokenId = ref<string | null>(localStorage.getItem(TOKEN_ID_KEY))
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<User | null>(null)
  const isLoading = ref(false)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // admin?
  const isAdmin = computed(() => user.value?.role === 'admin')

  // Actions
  const clearAuthState = () => {
    tokenId.value = null
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_ID_KEY)
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  const verifySession = async () => {
    try {
      authService.verify()
      const ok = await verify()

      if (!ok) {
        clearAuthState()
        return false
      }
      await getCurrentUser()
      return true
    } catch (e) {
      clearAuthState()
      return false
    }
  }

  const setTokenId = (newTokenId: string) => {
    tokenId.value = newTokenId
    localStorage.setItem(TOKEN_ID_KEY, newTokenId)
  }

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
  }

  const login = async (username: string, password: string) => {
    isLoading.value = true
    try {
      const response = await authService.login(username, password)
      if (!response.data.token_id || !response.data.token) {
        throw new Error('登入失敗，無效的憑證')
      }
      setTokenId(response.data.token_id)
      setToken(response.data.token)

      // 登入成功後獲取使用者資訊
      await getCurrentUser()
    } catch (error: unknown) {
      clearAuthState()
      const err = error as { response?: { data?: { detail?: string } } }
      throw new Error(err.response?.data?.detail || '登入失敗')
    } finally {
      isLoading.value = false
    }
  }

  const register = async (username: string, password: string, email?: string, phone?: string) => {
    isLoading.value = true
    try {
      const response = await authService.register({ username, password, email, phone })
      return response.data
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } }
      throw new Error(err.response?.data?.detail || '註冊失敗')
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    isLoading.value = true

    // 先保存 tokenId 以便後續使用
    const currentTokenId = tokenId.value

    // 立即清除本地數據，避免用戶等待
    clearAuthState()

    // 嘗試通知後端登出（不影響前端狀態）
    if (currentTokenId) {
      try {
        await authService.logout(currentTokenId)
      } catch (error) {
        // 忽略後端錯誤，因為本地數據已經清除
        console.warn('後端登出請求失敗，但本地數據已清除:', error)
      }
    }

    isLoading.value = false
  }

  const getCurrentUser = async () => {
    if (!token.value) return

    try {
      const response = await authService.getCurrentUser()
      user.value = response.data
      localStorage.setItem(USER_KEY, JSON.stringify(response.data))
    } catch (error) {
      console.error('獲取使用者資訊失敗:', error)
      // 如果獲取失敗，清除認證狀態
      clearAuthState()
      throw error
    }
  }

  const resetPassword = async (username: string, email: string) => {
    isLoading.value = true
    try {
      const response = await authService.resetPassword(username, email)
      return response.data
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } }
      throw new Error(err.response?.data?.detail || '重設密碼失敗')
    } finally {
      isLoading.value = false
    }
  }

  const verify = async () => {
    isLoading.value = true
    try {
      const response = await authService.verify()
      return response.data
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } }
      throw new Error(err.response?.data?.detail || '驗證失敗')
    } finally {
      isLoading.value = false
    }
  }

  const initializeAuth = () => {
    const savedToken = localStorage.getItem(TOKEN_KEY)
    const savedUser = localStorage.getItem(USER_KEY)

    if (savedToken && savedUser) {
      token.value = savedToken
      try {
        user.value = JSON.parse(savedUser)
      } catch (error) {
        console.error('解析使用者資料失敗:', error)
        logout()
      }
    }
    if (token.value) {
      void verifySession()
    }
  }

  const initAuth = async () => {
    initializeAuth()
    if (!token.value) return
    try {
      await verify()
      if (!user.value) {
        await getCurrentUser()
      }
    } catch (error) {
      clearAuthState()
    }
  }

  // 初始化認證狀態
  void initAuth()

  return {
    // State
    tokenId,
    token,
    user,
    isLoading,
    // Computed
    isAuthenticated,
    isAdmin,
    // Actions
    login,
    register,
    logout,
    getCurrentUser,
    resetPassword,
    verify,
    verifySession,
    initializeAuth,
    setTokenId,
    setToken,
  }
})
