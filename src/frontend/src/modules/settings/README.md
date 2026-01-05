# 設定模組 (Settings Module)

此模組提供使用者設定功能，包括個人資料、安全設定、偏好設定等。

## 目錄結構

```
settings/
├── index.ts                 # 模組匯出
├── services/
│   └── settings.ts         # API 服務層
├── stores/
│   └── settings.ts         # Pinia Store (狀態管理)
├── types/
│   └── index.ts            # TypeScript 型別定義
└── views/
    └── SettingsPage.vue     # 設定頁面
```

## 功能

### 1. 個人資料管理
- 基本資料編輯
- 聯絡資訊更新
- 地址管理

### 2. 安全設定
- 修改密碼
- 雙因素驗證
- 登入裝置管理
- 通知設定

### 3. 偏好設定
- 語言設定
- 主題設定
- 通知偏好
- 交易限額

### 4. 隱私設定
- 資料分享
- Cookie 設定
- 行銷偏好

## 使用方式

### 在元件中使用 Settings Store

```typescript
import { useSettingsStore } from '@/modules/settings'

const settingsStore = useSettingsStore()

// 取得個人資料
await settingsStore.fetchProfile()

// 更新個人資料
await settingsStore.updateProfile(profileData)

// 修改密碼
await settingsStore.changePassword(oldPassword, newPassword)

// 啟用雙因素驗證
await settingsStore.enable2FA()
```

## API 端點

- `GET /settings/profile` - 取得個人資料
- `PUT /settings/profile` - 更新個人資料
- `POST /settings/password` - 修改密碼
- `GET /settings/security` - 取得安全設定
- `POST /settings/2fa/enable` - 啟用雙因素驗證
- `GET /settings/preferences` - 取得偏好設定
- `PUT /settings/preferences` - 更新偏好設定

## 型別定義

查看 `types/index.ts` 瞭解完整的型別定義。
