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
  const isAuthenticated = computed(() => !!token.value && !!user.value && verify())

  // Actions
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
      setTokenId(response.data.token_id)
      setToken(response.data.token)
      
      // 登入成功後獲取使用者資訊
      await getCurrentUser()
    } catch (error: unknown) {
      tokenId.value = null
      token.value = null
      user.value = null
      localStorage.removeItem(TOKEN_ID_KEY)
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      const err = error as { response?: { data?: { detail?: string } } }
      throw new Error(err.response?.data?.detail || '登入失敗')
    } finally {
      isLoading.value = false
    }
  }

  const register = async (username: string, password: string, email?: string) => {
    isLoading.value = true
    try {
      const response = await authService.register({ username, password, email })
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
    try {
      if (tokenId.value) {
        await authService.logout(tokenId.value)
      }
    } catch (error) {
      console.error('登出時發生錯誤:', error)
    } finally {
      tokenId.value = null
      token.value = null
      user.value = null
      localStorage.removeItem(TOKEN_ID_KEY)
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      isLoading.value = false
    }
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
      await logout()
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
  }

  // 初始化認證狀態
  initializeAuth()

  return {
    // State
    tokenId,
    token,
    user,
    isLoading,
    // Computed
    isAuthenticated,
    // Actions
    login,
    register,
    logout,
    getCurrentUser,
    resetPassword,
    verify,
    initializeAuth,
    setTokenId,
    setToken,
  }
})
