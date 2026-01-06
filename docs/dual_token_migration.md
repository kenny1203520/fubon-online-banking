# 雙 Token 機制遷移指南
# Dual Token Mechanism Migration Guide

## 概述 (Overview)

本文檔說明從單 Token 系統遷移到雙 Token 機制（Access Token + Refresh Token）的數據庫架構變更和實施細節。

This document describes the database schema changes and implementation details for migrating from a single token system to a dual token mechanism (Access Token + Refresh Token).

## 變更內容 (Changes)

### 1. SessionModel 架構變更 (Schema Changes)

#### 舊架構 (Old Schema)
```python
class SessionModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    token: str = Field(index=True)  # 單一 token
    created_at: str
    expires_at: str  # 單一過期時間
```

#### 新架構 (New Schema)
```python
class SessionModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    token_id: str = Field(index=True, default_factory=lambda: str(uuid.uuid4()))
    access_token: str = Field(index=True)  # 短期 token (10 分鐘)
    refresh_token: str = Field(index=True)  # 長期 token (7 天)
    access_token_expires_at: str  # Access token 過期時間
    refresh_token_expires_at: str  # Refresh token 過期時間
    created_at: str
    revoked: bool = Field(default=False)  # 撤銷標記
```

### 2. 新增欄位說明 (New Fields)

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| `token_id` | str (UUID) | 唯一標識符，用於追蹤和撤銷 token |
| `access_token` | str | 短期訪問令牌（10分鐘有效） |
| `refresh_token` | str | 長期刷新令牌（7天有效） |
| `access_token_expires_at` | str (ISO datetime) | Access token 過期時間 |
| `refresh_token_expires_at` | str (ISO datetime) | Refresh token 過期時間 |
| `revoked` | bool | Token 是否已被撤銷（軟刪除） |

### 3. 刪除欄位 (Removed Fields)
- `token` - 被 `access_token` 和 `refresh_token` 取代
- `expires_at` - 被 `access_token_expires_at` 和 `refresh_token_expires_at` 取代

## 安全性改進 (Security Improvements)

### 1. 雙 Token 機制 (Dual Token Mechanism)
- **Access Token**:
  - 有效期：10 分鐘
  - 用於 API 請求驗證
  - 透過 `Authorization: Bearer <access_token>` header 傳遞
  - 短期有效降低被盜用風險

- **Refresh Token**:
  - 有效期：7 天
  - 儲存在 HttpOnly Cookie 中
  - 用於自動換發新 Access Token
  - 無法被 JavaScript 訪問（防止 XSS 攻擊）

### 2. bcrypt 密碼加密 (Password Hashing)
- 替換 `werkzeug.security` 為 `bcrypt`
- 使用 12 rounds salt 提供更強的加密保護
- 新函數：
  - `hash_password(password: str) -> str`
  - `verify_password(plain_password: str, hashed_password: str) -> bool`

### 3. HttpOnly Cookie 設定 (Cookie Configuration)
```python
response.set_cookie(
    key="refresh_token",
    value=tokens["refresh_token"],
    max_age=604800,  # 7 天（秒）
    httponly=True,   # 防止 JavaScript 訪問
    secure=True,     # 僅通過 HTTPS 發送
    samesite="strict"  # 防止 CSRF 攻擊
)
```

### 4. Token 撤銷機制 (Token Revocation)
- 使用 `token_id` 追蹤每個 session
- 登出時設置 `revoked=True`（軟刪除）
- 驗證時檢查 `revoked` 標記
- 保留記錄用於審計

## API 端點變更 (API Endpoint Changes)

### 1. POST `/api/v1/auth/login` - 登入
#### 請求 (Request)
```json
{
  "username": "user",
  "password": "password"
}
```

#### 響應 (Response)
```json
{
  "token": "access_token_here",
  "token_id": "uuid-here",
  "expires_in": 600,
  "message": "登入成功",
  "code": 200
}
```

#### Cookie 設定
- `refresh_token`: HttpOnly, Secure, SameSite=strict
- Max-Age: 604800 秒（7天）

### 2. POST `/api/v1/auth/logout` - 登出
#### 請求 (Request)
```json
{
  "token_id": "uuid-here"
}
```

#### 響應 (Response)
```json
{
  "message": "登出成功",
  "code": 200
}
```

#### 副作用
- 撤銷 session（設置 `revoked=True`）
- 清除 `refresh_token` cookie

### 3. POST `/api/v1/auth/refresh` - 刷新 Token (新增)
#### 請求 (Request)
- 從 Cookie 中自動讀取 `refresh_token`
- 無需 body

#### 響應 (Response)
```json
{
  "access_token": "new_access_token_here",
  "expires_in": 600,
  "message": "令牌刷新成功",
  "code": 200
}
```

## 數據庫遷移步驟 (Database Migration Steps)

### 選項 1: 全新部署 (Fresh Deployment)
1. 刪除現有 `sessionmodel` 表
2. 啟動應用程式讓 SQLModel 自動創建新表
3. 所有用戶需要重新登入

```sql
DROP TABLE IF EXISTS sessionmodel;
```

### 選項 2: 保留用戶登入狀態 (Preserve Sessions)
**不建議** - 因為架構變更過大，建議使用選項 1

## 前端整合 (Frontend Integration)

### 1. Axios 攔截器 (Interceptor)
```typescript
// Request Interceptor - 添加 Access Token
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response Interceptor - 自動刷新 Token
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        // 使用 refresh token 獲取新 access token
        const { data } = await axios.post('/api/v1/auth/refresh')
        localStorage.setItem('access_token', data.access_token)
        
        // 重試原請求
        error.config.headers.Authorization = `Bearer ${data.access_token}`
        return axios(error.config)
      } catch {
        // Refresh 失敗，跳轉登入頁
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)
```

### 2. 登入流程 (Login Flow)
```typescript
const login = async (username: string, password: string) => {
  const response = await axios.post('/api/v1/auth/login', { username, password })
  
  // 儲存 access token 到 localStorage
  localStorage.setItem('access_token', response.data.token)
  localStorage.setItem('token_id', response.data.token_id)
  
  // refresh_token 已自動存在 HttpOnly Cookie 中
  return response.data
}
```

### 3. 登出流程 (Logout Flow)
```typescript
const logout = async () => {
  const tokenId = localStorage.getItem('token_id')
  await axios.post('/api/v1/auth/logout', { token_id: tokenId })
  
  // 清除本地存儲
  localStorage.clear()
  
  // Cookie 已自動清除
  window.location.href = '/login'
}
```

## 核心函數 (Core Functions)

### core/auth.py

1. **create_user_tokens(user_id: int, session: Session)**
   - 創建雙 Token（Access + Refresh）
   - 生成唯一 token_id
   - 存儲到數據庫

2. **verify_access_token(token: str, session: Session)**
   - 驗證 Access Token 有效性
   - 檢查過期時間
   - 檢查撤銷狀態

3. **verify_refresh_token(token: str, session: Session)**
   - 驗證 Refresh Token 有效性
   - 返回 token_id 用於 token 旋轉

4. **rotate_tokens(token_id: str, session: Session)**
   - 使用 Refresh Token 生成新 Access Token
   - 更新數據庫中的 access_token

5. **revoke_token(token_id: str, session: Session)**
   - 撤銷指定 token（登出時調用）
   - 設置 revoked=True

## 測試計劃 (Testing Plan)

### 1. 註冊測試
- [ ] 註冊新用戶
- [ ] 驗證密碼使用 bcrypt 加密
- [ ] 確認可以正常登入

### 2. 登入測試
- [ ] 登入成功返回 access_token 和 token_id
- [ ] refresh_token 存在於 HttpOnly Cookie
- [ ] Cookie 設定包含 Secure 和 SameSite=strict

### 3. API 訪問測試
- [ ] 使用 Access Token 訪問受保護端點
- [ ] Access Token 過期後（10分鐘）返回 401
- [ ] 無效 token 返回 401

### 4. Token 刷新測試
- [ ] 使用 refresh endpoint 獲取新 access_token
- [ ] Refresh token 不存在時返回 401
- [ ] Refresh token 過期時返回 401

### 5. 登出測試
- [ ] 登出後 token 被撤銷
- [ ] refresh_token cookie 被清除
- [ ] 無法使用已撤銷的 token

### 6. Swagger UI 測試
- [ ] 可以在 /docs 頁面登入
- [ ] Authorize 按鈕可以設置 token
- [ ] 測試受保護端點正常工作

## 依賴更新 (Dependencies)

requirements.txt 中已包含以下依賴：
- `passlib[bcrypt]>=1.7.4` - bcrypt 密碼加密
- `PyJWT>=2.8.0` - JWT token（已安裝但當前未使用）
- `cryptography>=41.0.0` - 加密庫

## 總結 (Summary)

此次遷移實現了以下安全改進：

✅ 雙 Token 機制（Access + Refresh）  
✅ bcrypt 密碼加密  
✅ HttpOnly Cookie（防止 XSS）  
✅ SameSite=strict（防止 CSRF）  
✅ Token 撤銷機制  
✅ Token 過期自動刷新  

這些改進大幅提升了系統的安全性，符合現代 Web 應用的最佳實踐。
