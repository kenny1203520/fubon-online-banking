# 貸款模組 (Loan Module)

此模組提供完整的貸款服務功能，包括貸款申請、還款管理等。

## 目錄結構

```
loans/
├── index.ts                 # 模組匯出
├── services/
│   └── loan.ts             # API 服務層
├── stores/
│   └── loan.ts             # Pinia Store (狀態管理)
├── types/
│   └── index.ts            # TypeScript 型別定義
└── views/
    └── LoansPage.vue        # 貸款頁面
```

## 功能

### 1. 貸款產品瀏覽
- 個人信貸
- 房屋貸款
- 汽車貸款
- 企業貸款

### 2. 貸款申請
- 線上申請
- 試算功能
- 進度查詢

### 3. 貸款管理
- 貸款列表
- 還款記錄
- 提前還款
- 展延申請

## 使用方式

### 在元件中使用 Loan Store

```typescript
import { useLoanStore } from '@/modules/loans'

const loanStore = useLoanStore()

// 取得貸款產品
await loanStore.fetchLoanProducts()

// 申請貸款
await loanStore.applyLoan(loanData)

// 取得我的貸款
await loanStore.fetchMyLoans()
```

## API 端點

- `GET /loans/products` - 取得貸款產品列表
- `GET /loans` - 取得我的貸款
- `POST /loans/apply` - 申請貸款
- `POST /loans/:id/repay` - 還款
- `GET /loans/:id/schedule` - 取得還款計劃

## 型別定義

查看 `types/index.ts` 瞭解完整的型別定義。
