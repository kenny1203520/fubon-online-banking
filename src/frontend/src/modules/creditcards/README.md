# 信用卡模組 (Credit Card Module)

此模組提供完整的信用卡管理功能，包括信用卡列表、申請、明細查詢等。

## 目錄結構

```
creditcards/
├── index.ts                 # 模組匯出
├── services/
│   └── creditcard.ts       # API 服務層
├── stores/
│   └── creditcard.ts       # Pinia Store (狀態管理)
├── types/
│   └── index.ts            # TypeScript 型別定義
└── views/
    ├── CardListPage.vue     # 信用卡列表頁面
    ├── CardDetailPage.vue   # 信用卡明細頁面
    └── ApplyCardPage.vue    # 申請信用卡頁面
```

## 功能

### 1. 信用卡列表
- 顯示所有信用卡
- 顯示卡片狀態、額度、可用額度
- 快速操作（查看明細、繳費）

### 2. 信用卡明細
- 查看單張信用卡詳細資訊
- 消費記錄
- 帳單資訊
- 分期資訊

### 3. 申請信用卡
- 線上申請新卡
- 選擇卡片類型
- 填寫申請資料
- 提交審核

### 4. 信用卡繳費
- 查看帳單
- 繳費功能
- 自動扣款設定

## 使用方式

### 在元件中使用 Credit Card Store

```typescript
import { useCreditCardStore } from '@/modules/creditcards'

const cardStore = useCreditCardStore()

// 取得所有信用卡
await cardStore.fetchCards()

// 取得單張信用卡詳情
await cardStore.fetchCardById(cardId)

// 申請信用卡
await cardStore.applyCard(cardData)

// 繳費
await cardStore.payBill(billId, amount)
```

## API 端點

- `GET /cards` - 取得信用卡列表
- `GET /cards/:id` - 取得單張信用卡詳情
- `POST /cards/apply` - 申請信用卡
- `GET /cards/:id/transactions` - 取得消費記錄
- `GET /cards/:id/bills` - 取得帳單列表
- `POST /cards/:id/pay` - 繳費

## 型別定義

查看 `types/index.ts` 瞭解完整的型別定義。
