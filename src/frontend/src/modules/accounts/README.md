# 帳戶模組 (Accounts Module)

此模組提供完整的銀行帳戶管理功能，包括開戶申請、帳戶查詢、餘額管理及交易紀錄查看。

## 目錄結構

```
accounts/
├── index.ts                    # 模組匯出
├── services/
│   └── account.ts             # API 服務層
├── store/
│   └── account.ts             # Pinia Store (狀態管理)
├── types/
│   └── index.ts               # TypeScript 型別定義
└── views/
    ├── AccountListPage.vue     # 帳戶列表頁面
    ├── AccountDetailPage.vue   # 帳戶詳情頁面
    └── OpenAccountPage.vue     # 開戶申請頁面
```

## 功能

### 1. 帳戶列表 (Account List)
- 分頁顯示所有帳戶
- 帳戶統計資訊（總帳戶數、有效帳戶、總餘額）
- 快速查看帳戶狀態和餘額
- 刷新單一帳戶餘額
- 支援無現金提款標示

### 2. 帳戶詳情 (Account Detail)
- 完整的帳戶資訊展示
- 即時餘額查詢
- 無現金提款功能開關
- 交易紀錄查看（分頁）
- Tab 切換（基本資訊 / 交易紀錄）

### 3. 開戶申請 (Open Account)
- 線上開戶表單
- 欄位驗證（姓名、身分證號、電子郵件、初始存款）
- 身分證號格式驗證（台灣身分證）
- 服務條款同意確認
- 申請狀態追蹤

### 4. 餘額管理 (Balance Management)
- 查詢帳戶餘額
- 即時餘額更新
- 餘額顯示格式化

### 5. 無現金提款 (Cashless Withdrawal)
- 啟用/停用無現金提款功能
- 狀態即時更新

### 6. 交易紀錄 (Transactions)
- 查看帳戶交易紀錄
- 交易類型分類（存款、提款、轉帳）
- 交易時間和金額顯示
- 支援分頁查詢

## 使用方式

### 在元件中使用 Account Store

```typescript
import { useAccountStore } from '@/modules/accounts/store/account'

const accountStore = useAccountStore()

// 取得帳戶列表（分頁）
await accountStore.fetchAccounts(1, 10)

// 取得單一帳戶詳情
const account = await accountStore.fetchAccountById(accountId)

// 開戶申請
await accountStore.openAccount({
  full_name: '王小明',
  id_number: 'A123456789',
  email: 'example@email.com',
  initial_deposit: 5000
})

// 查詢餘額
await accountStore.getBalance(accountId)

// 設定無現金提款
await accountStore.setCashless(accountId, true)

// 取得交易紀錄
await accountStore.fetchTransactions(accountId, {
  page: 1,
  per_page: 10,
  type: 'deposit'
})

// 檢查是否有帳戶
const hasAccounts = accountStore.hasAccounts

// 取得有效帳戶
const activeAccounts = accountStore.activeAccounts

// 計算總餘額
const totalBalance = accountStore.totalBalance
```

### 直接使用 Account Service

```typescript
import { accountService } from '@/modules/accounts/services/account'

// 取得帳戶列表
const response = await accountService.getAccounts(1, 10)

// 開戶申請
const result = await accountService.openAccount({
  full_name: '王小明',
  id_number: 'A123456789',
  initial_deposit: 5000
})
```

### 路由配置範例

```typescript
const routes = [
  {
    path: '/accounts',
    name: 'AccountList',
    component: () => import('@/modules/accounts/views/AccountListPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/accounts/open',
    name: 'OpenAccount',
    component: () => import('@/modules/accounts/views/OpenAccountPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/accounts/:id',
    name: 'AccountDetail',
    component: () => import('@/modules/accounts/views/AccountDetailPage.vue'),
    meta: { requiresAuth: true }
  }
]
```

## API 端點

- `POST /accounts/open` - 開戶申請
- `GET /accounts` - 取得帳戶列表（分頁）
- `GET /accounts/{id}` - 取得單一帳戶資訊
- `POST /accounts/balance` - 查詢帳戶餘額
- `POST /accounts/cashless` - 設定無現金提款功能
- `POST /accounts/transactions` - 取得帳戶交易紀錄
- `PUT /accounts/{id}` - 更新帳戶資訊
- `DELETE /accounts/{id}` - 刪除/關閉帳戶

## 型別定義

所有的 TypeScript 型別都定義在 `types/index.ts` 中，包括：

### Account 相關
- `Account` - 帳戶完整資訊
- `AccountCreate` - 開戶申請資料
- `AccountResponse` - API 回應的帳戶資料
- `AccountList` - 帳戶列表（含分頁資訊）

### Balance 相關
- `BalanceRequest` - 餘額查詢請求
- `BalanceResponse` - 餘額查詢回應

### Cashless 相關
- `CashlessRequest` - 無現金提款設定請求
- `CashlessResponse` - 無現金提款設定回應

### Transaction 相關
- `Transaction` - 交易紀錄
- `TransactionResponse` - API 回應的交易資料
- `TransactionList` - 交易紀錄列表（含分頁資訊）
- `TransactionFilters` - 交易篩選條件

### State 相關
- `AccountState` - Store 狀態結構

## 帳戶狀態

帳戶有以下幾種狀態：
- `pending` - 待審核
- `active` - 正常（可使用）
- `inactive` - 停用
- `closed` - 已關閉

## 交易類型

支援以下交易類型：
- `deposit` - 存款
- `withdrawal` - 提款
- `transfer` - 轉帳

## 驗證規則

### 開戶申請驗證
- **姓名**：至少 2 個字元
- **身分證號**：台灣身分證格式（首位大寫英文 + 9 位數字）
- **電子郵件**：選填，但需符合 email 格式
- **初始存款**：最低 1,000 元，最高 10,000,000 元
- **服務條款**：必須同意

## 錯誤處理

所有的 API 呼叫都包含錯誤處理，並會拋出包含錯誤訊息的 Error 物件。建議在元件中使用 try-catch 來處理這些錯誤。

```typescript
try {
  await accountStore.openAccount(formData)
  // 成功處理
} catch (error) {
  errorMessage.value = error.message
}
```

## UI 特色

- 📊 視覺化的帳戶統計卡片
- 💳 美觀的帳戶卡片設計
- 🎨 狀態標籤顏色編碼
- 📱 響應式設計（支援手機版）
- ⚡ 即時餘額刷新
- 🔄 分頁支援
- 📝 完整的表單驗證
- ✨ 流暢的動畫效果

## 工具函數

模組內建多個工具函數：

- `formatCurrency()` - 格式化金額為新台幣格式
- `formatDate()` / `formatDateTime()` - 格式化日期時間
- `getStatusText()` - 取得狀態顯示文字
- `getStatusClass()` - 取得狀態樣式類別
- `getTransactionTypeText()` - 取得交易類型文字
- `getTransactionTypeClass()` - 取得交易類型樣式
- `validateIdNumber()` - 驗證身分證號格式
- `validateEmail()` - 驗證電子郵件格式

## 安全性考量

- 所有 API 請求都需要認證（JWT Token）
- 敏感資訊（身分證號）僅顯示部分
- 表單輸入驗證
- 防止重複提交
- XSS 防護

## 效能優化

- 分頁載入，避免一次載入大量資料
- 本地狀態快取
- 條件式資料載入（Tab 切換時才載入）
- 防抖處理（避免頻繁 API 呼叫）
