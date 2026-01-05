# 投資理財模組 (Investment Module)

此模組提供完整的投資理財功能，包括基金、股票、保險等投資商品管理。

## 目錄結構

```
investments/
├── index.ts                 # 模組匯出
├── services/
│   └── investment.ts       # API 服務層
├── stores/
│   └── investment.ts       # Pinia Store (狀態管理)
├── types/
│   └── index.ts            # TypeScript 型別定義
└── views/
    ├── FundPage.vue         # 基金頁面
    ├── StockPage.vue        # 股票頁面
    └── InsurancePage.vue    # 保險頁面
```

## 功能

### 1. 基金投資
- 基金列表查詢
- 基金申購/贖回
- 持有基金查詢
- 損益分析

### 2. 股票交易
- 股票查詢
- 買賣下單
- 持股查詢
- 即時報價

### 3. 保險商品
- 保險商品瀏覽
- 線上投保
- 保單查詢
- 保費繳納

### 4. 投資組合
- 資產配置
- 績效分析
- 風險評估

## 使用方式

### 在元件中使用 Investment Store

```typescript
import { useInvestmentStore } from '@/modules/investments'

const investmentStore = useInvestmentStore()

// 取得基金列表
await investmentStore.fetchFunds()

// 申購基金
await investmentStore.purchaseFund(fundId, amount)

// 取得持股
await investmentStore.fetchHoldings()
```

## API 端點

- `GET /investments/funds` - 取得基金列表
- `GET /investments/funds/:id` - 取得基金詳情
- `POST /investments/funds/purchase` - 申購基金
- `POST /investments/funds/redeem` - 贖回基金
- `GET /investments/stocks` - 取得股票列表
- `GET /investments/holdings` - 取得持有投資商品

## 型別定義

查看 `types/index.ts` 瞭解完整的型別定義。
