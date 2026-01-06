# 認證模組 (Auth Module)

此模組提供完整的使用者認證功能，包括登入、註冊、登出及密碼重設。

## 目錄結構

```
auth/
├── index.ts                 # 模組匯出
├── services/
│   └── auth.ts             # API 服務層
├── store/
│   └── auth.ts             # Pinia Store (狀態管理)
├── types/
│   └── index.ts            # TypeScript 型別定義
└── views/
    ├── LoginPage.vue        # 登入頁面
    ├── RegisterPage.vue     # 註冊頁面
    └── ForgotPasswordPage.vue # 重設密碼頁面
```

## 功能

### 1. 登入 (Login)
- 使用者名稱和密碼驗證
- 自動儲存 token 和使用者資訊到 localStorage
- 支援重定向到原始頁面或儀表板

### 2. 註冊 (Register)
- 使用者帳號申請
- 欄位驗證（帳號長度、密碼強度、電子郵件格式）
- 密碼確認
- 服務條款同意確認

### 3. 登出 (Logout)
- 清除使用者 session
- 移除 localStorage 中的認證資訊

### 4. 密碼重設 (Reset Password)
- 透過電子郵件發送重設連結
- 支援重新發送

## 使用方式

### 在元件中使用 Auth Store

```typescript
import { useAuthStore } from '@/modules/auth/store/auth'

const authStore = useAuthStore()

// 登入
await authStore.login('username', 'password')

// 註冊
await authStore.register('username', 'password', 'email@example.com')

// 登出
await authStore.logout()

// 檢查是否已登入
const isLoggedIn = authStore.isAuthenticated

// 取得當前使用者
const currentUser = authStore.user
```

### 路由守衛範例

```typescript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})
```

### 直接使用 Auth Service

```typescript
import { authService } from '@/modules/auth/services/auth'

// 直接呼叫 API
const response = await authService.login('username', 'password')
```

## API 端點

- `POST /auth/login` - 使用者登入
- `POST /auth/register` - 使用者註冊
- `POST /auth/logout` - 使用者登出
- `GET /auth/me` - 取得當前使用者資訊
- `POST /auth/refresh` - 刷新 token
- `POST /auth/reset-password` - 重設密碼

## 型別定義

所有的 TypeScript 型別都定義在 `types/index.ts` 中，包括：

- `LoginRequest` / `LoginResponse`
- `RegisterRequest` / `RegisterResponse`
- `LogoutRequest` / `LogoutResponse`
- `User`
- `AuthState`

## 持久化

認證資訊會自動儲存在 localStorage：
- `auth_token` - JWT token
- `auth_user` - 使用者資訊

在應用初始化時，store 會自動從 localStorage 恢復認證狀態。

## 錯誤處理

所有的 API 呼叫都包含錯誤處理，並會拋出包含錯誤資訊的 Error 物件。建議在元件中使用 try-catch 來處理這些錯誤。

```typescript
try {
  await authStore.login(username.value, password.value)
  router.push('/dashboard')
} catch (error) {
  errorMessage.value = error.message
}
```

## 安全性

- 密碼不會以明文儲存
- Token 儲存在 localStorage
- 所有 API 請求都會自動帶入 token（由 axios interceptor 處理）
- 當 token 失效時會自動清除認證狀態
