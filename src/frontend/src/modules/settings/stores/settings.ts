import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { settingsService } from '../services/settings'
import type {
  UserProfile,
  SecuritySettings,
  Preferences,
  PasswordChangeRequest,
  ProfileUpdateRequest,
  TwoFactorVerification,
  NotificationSettings,
  PrivacySettings
} from '../types'

export const useSettingsStore = defineStore('settings', () => {
  // State
  const profile = ref<UserProfile | null>(null)
  const security = ref<SecuritySettings | null>(null)
  const preferences = ref<Preferences | null>(null)
  const notifications = ref<NotificationSettings | null>(null)
  const privacy = ref<PrivacySettings | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const has2FAEnabled = computed(() => 
    security.value?.has_2fa_enabled ?? false
  )
  
  const preferredLanguage = computed(() => 
    preferences.value?.language ?? 'zh-TW'
  )
  
  const preferredTheme = computed(() => 
    preferences.value?.theme ?? 'light'
  )
  
  const dailyTransferLimit = computed(() => 
    preferences.value?.transaction_limits.daily_transfer_limit ?? 0
  )
  
  const trustedDeviceCount = computed(() => 
    security.value?.trusted_devices.length ?? 0
  )

  // Actions
  /**
   * 取得個人資料
   */
  const fetchProfile = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.getProfile()
      profile.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得個人資料失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新個人資料
   */
  const updateProfile = async (data: ProfileUpdateRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.updateProfile(data)
      profile.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '更新個人資料失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 修改密碼
   */
  const changePassword = async (data: PasswordChangeRequest) => {
    isLoading.value = true
    error.value = null

    try {
      await settingsService.changePassword(data)
      // 更新安全設定以反映密碼變更時間
      await fetchSecuritySettings()
    } catch (err) {
      const message = err instanceof Error ? err.message : '修改密碼失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得安全設定
   */
  const fetchSecuritySettings = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.getSecuritySettings()
      security.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得安全設定失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 啟用雙因素驗證
   */
  const enable2FA = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.enable2FA()
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '啟用雙因素驗證失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 驗證並啟用雙因素驗證
   */
  const verify2FA = async (data: TwoFactorVerification) => {
    isLoading.value = true
    error.value = null

    try {
      await settingsService.verify2FA(data)
      // 重新取得安全設定
      await fetchSecuritySettings()
    } catch (err) {
      const message = err instanceof Error ? err.message : '驗證雙因素驗證失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 停用雙因素驗證
   */
  const disable2FA = async () => {
    isLoading.value = true
    error.value = null

    try {
      await settingsService.disable2FA()
      // 重新取得安全設定
      await fetchSecuritySettings()
    } catch (err) {
      const message = err instanceof Error ? err.message : '停用雙因素驗證失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 移除信任裝置
   */
  const removeTrustedDevice = async (deviceId: string) => {
    isLoading.value = true
    error.value = null

    try {
      await settingsService.removeTrustedDevice(deviceId)
      // 重新取得安全設定
      await fetchSecuritySettings()
    } catch (err) {
      const message = err instanceof Error ? err.message : '移除裝置失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得偏好設定
   */
  const fetchPreferences = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.getPreferences()
      preferences.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得偏好設定失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新偏好設定
   */
  const updatePreferences = async (data: Partial<Preferences>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.updatePreferences(data)
      preferences.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '更新偏好設定失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得通知設定
   */
  const fetchNotificationSettings = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.getNotificationSettings()
      notifications.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得通知設定失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新通知設定
   */
  const updateNotificationSettings = async (data: Partial<NotificationSettings>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.updateNotificationSettings(data)
      notifications.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '更新通知設定失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 取得隱私設定
   */
  const fetchPrivacySettings = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.getPrivacySettings()
      privacy.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '取得隱私設定失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新隱私設定
   */
  const updatePrivacySettings = async (data: Partial<PrivacySettings>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await settingsService.updatePrivacySettings(data)
      privacy.value = response.data
      return response.data
    } catch (err) {
      const message = err instanceof Error ? err.message : '更新隱私設定失敗'
      error.value = message
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 載入所有設定
   */
  const loadAllSettings = async () => {
    await Promise.all([
      fetchProfile(),
      fetchSecuritySettings(),
      fetchPreferences(),
      fetchNotificationSettings(),
      fetchPrivacySettings()
    ])
  }

  /**
   * 清空錯誤訊息
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * 重置狀態
   */
  const reset = () => {
    profile.value = null
    security.value = null
    preferences.value = null
    notifications.value = null
    privacy.value = null
    error.value = null
  }

  return {
    // State
    profile,
    security,
    preferences,
    notifications,
    privacy,
    isLoading,
    error,
    
    // Computed
    has2FAEnabled,
    preferredLanguage,
    preferredTheme,
    dailyTransferLimit,
    trustedDeviceCount,
    
    // Actions
    fetchProfile,
    updateProfile,
    changePassword,
    fetchSecuritySettings,
    enable2FA,
    verify2FA,
    disable2FA,
    removeTrustedDevice,
    fetchPreferences,
    updatePreferences,
    fetchNotificationSettings,
    updateNotificationSettings,
    fetchPrivacySettings,
    updatePrivacySettings,
    loadAllSettings,
    clearError,
    reset
  }
})
