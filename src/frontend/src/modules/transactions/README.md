# 交易模組 (Transactions Module)

此模組提供完整的交易管理功能，包括交易記錄查詢、轉帳、換匯等操作。

## 目錄結構

```
transactions/
├── index.ts                    # 模組匯出
├── services/
│   └── transaction.ts         # API 服務層
├── stores/
│   └── transaction.ts         # Pinia Store (狀態管理)
├── types/
│   └── index.ts               # TypeScript 型別定義
└── views/
    ├── HistoryPage.vue        # 交易記錄頁面
    └── ExchangePage.vue       # 換匯頁面
```

## 功能

### 1. 交易記錄 (Transaction History)
- 分頁顯示交易記錄
- 交易統計資訊（總交易數、總存款、總提款、淨額）
- 交易類型篩選（存款、提款、轉帳）
- 日期範圍篩選
- 交易詳情展示

### 2. 換匯 (Currency Exchange)
- 多種貨幣支援（TWD, USD, EUR, JPY, GBP, CNY, HKD, AUD, SGD, KRW）
- 即時匯率查詢
- 換匯計算器
- 匯率列表展示
- 換匯結果確認

### 3. 轉帳 (Transfer)
- 帳戶間轉帳
- 轉帳金額驗證
- 交易描述備註

## 使用方式

### 在元件中使用 Transaction Store

```typescript
import { useTransactionStore } from '@/modules/transactions/stores/transaction'

const transactionStore = useTransactionStore()

// 取得交易列表（分頁）
await transactionStore.fetchTransactions({
  account_id: 123,
  page: 1,
  per_page: 20,
  type: 'deposit',
  frm: '2024-01-01',
  to: '2024-12-31'
})

// 取得單一交易詳情
const transaction = await transactionStore.fetchTransactionById(456)

// 轉帳
await transactionStore.transfer({
  from_account_id: 123,
  to_account_id: 456,
  amount: 5000,
  description: '還款'
})

// 換匯
await transactionStore.exchange({
  from_currency: 'TWD',
  to_currency: 'USD',
  amount: 30000,
  account_id: 123
})

// 取得匯率
await transactionStore.fetchExchangeRates('TWD')

// 取得特定帳戶的交易記錄
await transactionStore.fetchAccountTransactions(123, {
  type: 'transfer',
  page: 1,
  per_page: 10
})

// 檢查是否有交易記錄
const hasData = transactionStore.hasTransactions

// 計算統計資訊
const totalDeposits = transactionStore.depositTotal
const totalWithdrawals = transactionStore.withdrawalTotal
const netAmount = transactionStore.totalAmount
```

### 直接使用 Transaction Service

```typescript
import { transactionService } from '@/modules/transactions/services/transaction'

// 取得交易列表
const response = await transactionService.getTransactions({
  account_id: 123,
  page: 1,
  per_page: 20
})

// 轉帳
const result = await transactionService.transfer({
  from_account_id: 123,
  to_account_id: 456,
  amount: 5000
})

// 換匯
const exchangeResult = await transactionService.exchange({
  from_currency: 'TWD',
  to_currency: 'USD',
  amount: 30000
})

// 取得匯率
const rates = await transactionService.getExchangeRates('TWD')
```

### 路由配置範例

```typescript
const routes = [
  {
    path: '/transactions/history',
    name: 'TransactionHistory',
    component: () => import('@/modules/transactions/views/HistoryPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/transactions/exchange',
    name: 'Exchange',
    component: () => import('@/modules/transactions/views/ExchangePage.vue'),
    meta: { requiresAuth: true }
  }
]
```

## API 端點

- `GET /transactions` - 取得交易列表（分頁）
- `GET /transactions/{id}` - 取得單一交易詳情
- `POST /transactions/transfer` - 轉帳
- `POST /transactions/exchange` - 換匯
- `GET /transactions/exchange/rates` - 取得匯率

## 型別定義

所有的 TypeScript 型別都定義在 `types/index.ts` 中，包括：

### Transaction 相關
- `Transaction` - 交易完整資訊
- `TransactionResponse` - API 回應的交易資料
- `TransactionList` - 交易列表（含分頁資訊）
- `TransactionQuery` - 交易查詢參數
- `TransactionFilters` - 交易篩選條件

### Transfer 相關
- `TransferRequest` - 轉帳請求
- `TransferResponse` - 轉帳回應

### Exchange 相關
- `ExchangeRate` - 匯率資訊
- `ExchangeRequest` - 換匯請求
- `ExchangeResponse` - 換匯回應
- `ExchangeRateResponse` - 匯率列表回應

### State 相關
- `TransactionState` - Store 狀態結構

## 交易類型

支援以下交易類型：
- `deposit` - 存款
- `withdrawal` - 提款
- `transfer` - 轉帳

## 支援貨幣

模組支援以下貨幣：
- **TWD** - 新台幣 (NT$)
- **USD** - 美元 ($)
- **EUR** - 歐元 (€)
- **JPY** - 日圓 (¥)
- **GBP** - 英鎊 (£)
- **CNY** - 人民幣 (¥)
- **HKD** - 港幣 (HK$)
- **AUD** - 澳幣 (A$)
- **SGD** - 新加坡幣 (S$)
- **KRW** - 韓元 (₩)

## 驗證規則

### 換匯驗證
- **金額**：0 ~ 10,000,000
- **來源貨幣**：不可與目標貨幣相同
- **匯率**：必須有有效的匯率資料

### 轉帳驗證
- **金額**：必須大於 0
- **來源帳戶**：不可與目標帳戶相同
- **帳戶餘額**：來源帳戶餘額必須足夠

## 錯誤處理

所有的 API 呼叫都包含錯誤處理，並會拋出包含錯誤訊息的 Error 物件。建議在元件中使用 try-catch 來處理這些錯誤。

```typescript
try {
  await transactionStore.exchange(formData)
  // 成功處理
} catch (error) {
  errorMessage.value = error.message
}
```

## UI 特色

### 交易記錄頁面
- 📊 視覺化的交易統計卡片
- 🔍 強大的篩選功能（類型、日期範圍）
- 📋 清晰的交易列表表格
- 🎨 交易類型顏色編碼
- 💰 正負金額顯示（存款為正、提款為負）
- 🔄 分頁支援
- 📱 響應式設計

### 換匯頁面
- 💱 直覺的貨幣選擇器
- 🔄 快速貨幣交換按鈕
- 💵 即時金額預估
- 📈 當前匯率顯示
- ✅ 換匯結果確認卡片
- 📊 即時匯率表格
- 🎯 多貨幣支援

## 工具函數

模組內建多個工具函數：

### 交易記錄頁面
- `formatCurrency()` - 格式化金額（含貨幣符號）
- `formatDateTime()` - 格式化日期時間
- `getTypeText()` - 取得交易類型顯示文字
- `getTypeClass()` - 取得交易類型樣式類別
- `getAmountClass()` - 取得金額樣式（正/負）
- `getAmountPrefix()` - 取得金額前綴（+/-）

### 換匯頁面
- `formatCurrency()` - 格式化金額（含貨幣符號）
- `swapCurrencies()` - 交換來源和目標貨幣
- `validateAmount()` - 驗證金額範圍

## 安全性考量

- 所有 API 請求都需要認證（JWT Token）
- 金額驗證（範圍檢查）
- 防止重複提交
- 交易確認機制
- 錯誤訊息安全處理

## 效能優化

- 分頁載入，避免一次載入大量資料
- 本地狀態快取
- 條件式資料載入
- 防抖處理（避免頻繁 API 呼叫）
- 計算屬性優化（Computed）

## 統計資訊

交易記錄頁面提供以下統計資訊：
- **交易總數** - 總交易筆數
- **總存款** - 所有存款交易的總金額
- **總提款** - 所有提款交易的總金額
- **淨額** - 存款減去提款的淨值

## 篩選功能

### 交易類型篩選
- 全部
- 存款
- 提款
- 轉帳

### 日期篩選
- 起始日期
- 結束日期
- 日期範圍查詢

## 分頁功能

- 支援自訂每頁顯示筆數
- 上一頁 / 下一頁按鈕
- 當前頁碼 / 總頁數顯示
- 自動禁用無效的分頁按鈕

## 響應式設計

所有頁面都支援響應式設計：
- 桌面版（> 768px）：完整表格與多欄佈局
- 平板版（768px）：調整欄位寬度
- 手機版（< 768px）：單欄佈局、字體縮小、精簡表格

## 注意事項

1. **帳戶 ID**: 交易記錄查詢需要提供 `account_id`
2. **匯率更新**: 換匯前建議先呼叫 `fetchExchangeRates()` 取得最新匯率
3. **錯誤處理**: 所有操作都應包含 try-catch 錯誤處理
4. **金額精度**: 金額計算使用 2 位小數精度
5. **日期格式**: 日期使用 ISO 8601 格式（YYYY-MM-DD）

## 整合範例

```typescript
// 在 Dashboard 中整合交易模組
import { useTransactionStore } from '@/modules/transactions'
import { useAccountStore } from '@/modules/accounts'

const transactionStore = useTransactionStore()
const accountStore = useAccountStore()

// 載入帳戶和交易
onMounted(async () => {
  await accountStore.fetchAccounts()
  
  if (accountStore.accounts.length > 0) {
    const firstAccountId = accountStore.accounts[0].id
    await transactionStore.fetchAccountTransactions(firstAccountId)
  }
})
```
