import apiClient from '@/shared/services/api'
import type {
  UserProfile,
  SecuritySettings,
  Preferences,
  PasswordChangeRequest,
  ProfileUpdateRequest,
  TwoFactorSetup,
  TwoFactorVerification,
  NotificationSettings,
  PrivacySettings
} from '../types'

export const settingsService = {
  /**
   * 取得個人資料
   */
  getProfile: () => 
    apiClient.get<UserProfile>('/settings/profile'),
  
  /**
   * 更新個人資料
   */
  updateProfile: (data: ProfileUpdateRequest) => 
    apiClient.put<UserProfile>('/settings/profile', data),
  
  /**
   * 修改密碼
   */
  changePassword: (data: PasswordChangeRequest) => 
    apiClient.post('/settings/password', data),
  
  /**
   * 取得安全設定
   */
  getSecuritySettings: () => 
    apiClient.get<SecuritySettings>('/settings/security'),
  
  /**
   * 啟用雙因素驗證
   */
  enable2FA: () => 
    apiClient.post<TwoFactorSetup>('/settings/2fa/enable'),
  
  /**
   * 驗證並啟用雙因素驗證
   */
  verify2FA: (data: TwoFactorVerification) => 
    apiClient.post('/settings/2fa/verify', data),
  
  /**
   * 停用雙因素驗證
   */
  disable2FA: () => 
    apiClient.post('/settings/2fa/disable'),
  
  /**
   * 移除信任裝置
   */
  removeTrustedDevice: (deviceId: string) => 
    apiClient.delete(`/settings/devices/${deviceId}`),
  
  /**
   * 取得偏好設定
   */
  getPreferences: () => 
    apiClient.get<Preferences>('/settings/preferences'),
  
  /**
   * 更新偏好設定
   */
  updatePreferences: (data: Partial<Preferences>) => 
    apiClient.put<Preferences>('/settings/preferences', data),
  
  /**
   * 取得通知設定
   */
  getNotificationSettings: () => 
    apiClient.get<NotificationSettings>('/settings/notifications'),
  
  /**
   * 更新通知設定
   */
  updateNotificationSettings: (data: Partial<NotificationSettings>) => 
    apiClient.put<NotificationSettings>('/settings/notifications', data),
  
  /**
   * 取得隱私設定
   */
  getPrivacySettings: () => 
    apiClient.get<PrivacySettings>('/settings/privacy'),
  
  /**
   * 更新隱私設定
   */
  updatePrivacySettings: (data: Partial<PrivacySettings>) => 
    apiClient.put<PrivacySettings>('/settings/privacy', data),
}
