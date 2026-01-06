# 儀表板模組 (Dashboard Module)

此模組提供使用者主頁面的儀表板功能，顯示帳戶總覽和重要資訊。

## 目錄結構

```
dashboard/
├── index.ts                 # 模組匯出
├── services/
│   └── dashboard.ts        # API 服務層
├── stores/
│   └── dashboard.ts        # Pinia Store (狀態管理)
├── types/
│   └── index.ts            # TypeScript 型別定義
└── views/
    └── DashboardPage.vue    # 儀表板頁面
```

## 功能

### 1. 帳戶總覽
- 總資產顯示
- 各帳戶餘額
- 近期交易
- 快速操作按鈕

### 2. 信用卡資訊
- 信用卡列表
- 本期帳單
- 可用額度

### 3. 投資概況
- 投資組合總值
- 損益統計
- 持股列表

### 4. 快速連結
- 常用功能快速存取
- 最近使用的功能

### 5. 通知與提醒
- 重要資訊
- 到期提醒
- 系統公告

## 使用方式

### 在元件中使用 Dashboard Store

```typescript
import { useDashboardStore } from '@/modules/dashboard'

const dashboardStore = useDashboardStore()

// 取得儀表板資料
await dashboardStore.fetchDashboardData()

// 取得帳戶摘要
const summary = dashboardStore.accountSummary

// 取得最近交易
const recentTransactions = dashboardStore.recentTransactions
```

## API 端點

- `GET /dashboard/summary` - 取得儀表板摘要
- `GET /dashboard/accounts` - 取得帳戶概覽
- `GET /dashboard/transactions/recent` - 取得最近交易
- `GET /dashboard/notifications` - 取得通知

## 型別定義

查看 `types/index.ts` 瞭解完整的型別定義。
