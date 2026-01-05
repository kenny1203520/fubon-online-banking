export interface UserProfile {
  user_id: number
  username: string
  email: string
  phone: string
  full_name: string
  date_of_birth?: string
  gender?: 'male' | 'female' | 'other'
  id_number: string
  address?: Address
  created_at: string
  updated_at: string
}

export interface Address {
  postal_code: string
  city: string
  district: string
  street: string
  detail?: string
}

export interface SecuritySettings {
  has_2fa_enabled: boolean
  login_notifications: boolean
  transaction_notifications: boolean
  trusted_devices: TrustedDevice[]
  last_password_change: string
}

export interface TrustedDevice {
  device_id: string
  device_name: string
  device_type: 'mobile' | 'tablet' | 'desktop'
  last_used: string
  ip_address: string
  location?: string
}

export interface Preferences {
  language: 'zh-TW' | 'zh-CN' | 'en-US'
  theme: 'light' | 'dark' | 'auto'
  currency: 'TWD' | 'USD' | 'CNY'
  notification_channels: {
    email: boolean
    sms: boolean
    push: boolean
  }
  transaction_limits: {
    daily_transfer_limit: number
    single_transfer_limit: number
  }
}

export interface PasswordChangeRequest {
  old_password: string
  new_password: string
  confirm_password: string
}

export interface ProfileUpdateRequest {
  email?: string
  phone?: string
  full_name?: string
  address?: Address
}

export interface TwoFactorSetup {
  secret: string
  qr_code: string
  backup_codes: string[]
}

export interface TwoFactorVerification {
  code: string
}

export interface NotificationSettings {
  email_notifications: boolean
  sms_notifications: boolean
  push_notifications: boolean
  marketing_emails: boolean
  transaction_alerts: boolean
  security_alerts: boolean
  account_updates: boolean
}

export interface PrivacySettings {
  share_data_with_partners: boolean
  allow_marketing: boolean
  allow_analytics: boolean
  cookie_preferences: {
    necessary: boolean
    functional: boolean
    analytics: boolean
    marketing: boolean
  }
}

export interface SettingsState {
  profile: UserProfile | null
  security: SecuritySettings | null
  preferences: Preferences | null
  notifications: NotificationSettings | null
  privacy: PrivacySettings | null
  isLoading: boolean
  error: string | null
}
